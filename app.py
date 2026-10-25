"""MediGuide AI - Streamlit user interface."""

import json
import time

import streamlit as st

from src.cache_manager import cache_description, configure_cache
from src.chains import (
    build_assessment_chain,
    build_chat_assessment_messages,
    build_llm,
    message_demo,
    run_assessment,
    stream_narrative,
)
from src.config import (
    COMMON_SYMPTOMS,
    DURATION_OPTIONS,
    GENDER_OPTIONS,
    LANGUAGE_OPTIONS,
    MEDICAL_DISCLAIMER,
    OPENAI_MODEL,
)
from src.utils import (
    format_patient_summary,
    safe_parse_json,
    urgency_message,
)

st.set_page_config(
    page_title="MediGuide AI",
    page_icon="🩺",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Global safety notice: intentionally visible on the main screen.
# ---------------------------------------------------------------------------
st.error(
    "⚠️ MEDICAL SAFETY NOTICE — Educational AI prototype only. "
    "MediGuide AI is NOT a doctor, diagnosis service, emergency service, "
    "or replacement for qualified medical care. Never use it to confirm a diagnosis."
)

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.title("🩺 MediGuide AI")
    st.caption("AI-Powered Medical Symptom Assessment & Patient Guidance")

    st.warning(MEDICAL_DISCLAIMER)

    st.subheader("Model configuration")
    st.write(f"Model: `{OPENAI_MODEL}`")

    cache_choice = st.selectbox(
        "Caching",
        ["InMemoryCache", "SQLiteCache", "None"],
        help=(
            "InMemoryCache is fast but session-only. SQLiteCache stores responses "
            "on disk and can survive application restarts."
        ),
    )
    configure_cache(cache_choice)
    st.caption(cache_description(cache_choice))

    st.subheader("Language")
    sidebar_language = st.selectbox(
        "Default answer language",
        LANGUAGE_OPTIONS,
        index=0,
    )

    st.divider()
    st.info(
        "For severe or rapidly worsening symptoms, contact a qualified healthcare "
        "professional or emergency service immediately."
    )

# ---------------------------------------------------------------------------
# Main content
# ---------------------------------------------------------------------------
st.title("MediGuide AI")
st.write(
    "Enter basic information and symptoms to receive structured, "
    "safety-focused preliminary guidance."
)

st.info(
    "Possible conditions shown below are for education only. "
    "They are not confirmed diagnoses."
)

with st.form("medical_assessment_form"):
    st.subheader("Patient information")

    col1, col2 = st.columns(2)
    with col1:
        age = st.text_input(
            "Patient age *",
            placeholder="e.g. 25",
            help="Enter an age such as 25. The app does not require a name.",
        )
    with col2:
        gender = st.selectbox("Gender", GENDER_OPTIONS)

    st.subheader("Symptoms")
    selected_symptoms = st.multiselect(
        "Select symptoms *",
        COMMON_SYMPTOMS,
        help="Choose all relevant symptoms.",
    )
    symptom_notes = st.text_area(
        "Other symptom details (optional)",
        placeholder="Describe any additional symptoms or context...",
    )

    col3, col4 = st.columns(2)
    with col3:
        duration = st.selectbox("Duration of symptoms", DURATION_OPTIONS)
    with col4:
        severity = st.slider("Overall severity (1-10)", 1, 10, 3)

    st.subheader("Additional medical context")
    conditions = st.text_area(
        "Existing medical conditions",
        placeholder="e.g. asthma, diabetes, none known",
    )
    medications = st.text_area(
        "Current medications",
        placeholder="List current medicines if relevant",
    )
    notes = st.text_area(
        "Additional notes",
        placeholder="Anything else the healthcare professional should know...",
    )

    answer_language = st.selectbox(
        "Answer language",
        LANGUAGE_OPTIONS,
        index=LANGUAGE_OPTIONS.index(sidebar_language),
    )

    submitted = st.form_submit_button(
        "🔎 Assess Symptoms",
        type="primary",
        use_container_width=True,
    )

if submitted:
    # Requirement: empty symptoms must not call the API.
    if not selected_symptoms and not symptom_notes.strip():
        st.warning("Please enter at least one symptom before submitting.")
        st.stop()

    # Basic local validation.
    if not age.strip():
        st.warning("Please enter the patient's age.")
        st.stop()

    symptoms_text = ", ".join(selected_symptoms)
    if symptom_notes.strip():
        symptoms_text = (
            f"{symptoms_text}; Additional symptom details: {symptom_notes.strip()}"
            if symptoms_text
            else symptom_notes.strip()
        )

    inputs = {
        "age": age.strip(),
        "gender": gender,
        "symptoms": symptoms_text,
        "duration": duration,
        "severity": severity,
        "conditions": conditions.strip() or "None provided",
        "medications": medications.strip() or "None provided",
        "notes": notes.strip() or "None provided",
        "language": answer_language,
    }

    try:
        llm = build_llm()
        assessment_chain = build_assessment_chain(llm)
    except Exception as exc:
        st.error(f"Could not initialise the OpenAI model: {exc}")
        st.stop()

    # The same input + same model + same prompt can be served by LangChain cache.
    st.subheader("Assessment")
    summary_col, urgency_col = st.columns(2)

    with summary_col:
        st.metric("Reported severity", f"{severity}/10")
        st.write(format_patient_summary(inputs))

    with st.spinner("Preparing the structured assessment..."):
        started = time.perf_counter()
        try:
            raw_json = run_assessment(assessment_chain, inputs)
        except Exception as exc:
            st.error(
                "The assessment request failed. Check your API key, internet "
                f"connection, model configuration, and LangChain installation.\n\n{exc}"
            )
            st.stop()
        elapsed = time.perf_counter() - started

    parsed, parse_error = safe_parse_json(raw_json)

    if parsed is None:
        st.error("The model response could not be safely parsed.")
        st.info("The app did not crash. The raw model response is shown for debugging.")
        with st.expander("Raw model output"):
            st.code(raw_json or "(empty response)")
        st.stop()

    urgency = parsed["urgency_level"]

    with urgency_col:
        st.metric("Urgency level", urgency)
        if urgency == "EMERGENCY":
            st.error(f"🚨 {urgency_message(urgency)}")
        elif urgency == "HIGH":
            st.warning(f"⚠️ {urgency_message(urgency)}")
        elif urgency == "MEDIUM":
            st.warning(f"ℹ️ {urgency_message(urgency)}")
        else:
            st.success(f"✅ {urgency_message(urgency)}")

    st.caption(f"Structured assessment completed in approximately {elapsed:.2f} seconds.")

    # Results dashboard.
    tabs = st.tabs(
        [
            "Summary",
            "Possible conditions",
            "Next steps",
            "Questions for doctor",
            "Warning signs",
            "LangChain details",
        ]
    )

    with tabs[0]:
        st.subheader("Patient symptom summary")
        st.write(parsed["summary"])
        st.info(
            "This summary is generated guidance, not a medical diagnosis. "
            "Please discuss concerns with a qualified healthcare professional."
        )

    with tabs[1]:
        st.subheader("Possible conditions — education only")
        if parsed["possible_conditions"]:
            for item in parsed["possible_conditions"]:
                if isinstance(item, dict):
                    name = item.get("name", "Unspecified")
                    reason = item.get("reason", "No explanation provided.")
                    with st.expander(name):
                        st.write(reason)
                        st.caption("Educational possibility only — not a confirmed diagnosis.")
                else:
                    st.write(str(item))
        else:
            st.write("No educational possibilities were returned.")

    with tabs[2]:
        st.subheader("Recommended next steps")
        for item in parsed["recommended_next_steps"]:
            st.write(f"• {item}")

    with tabs[3]:
        st.subheader("Questions to ask a healthcare professional")
        for item in parsed["questions_for_doctor"]:
            st.write(f"• {item}")

    with tabs[4]:
        st.subheader("Warning signs requiring immediate attention")
        if parsed["warning_signs"]:
            for item in parsed["warning_signs"]:
                st.error(f"🚨 {item}")
        else:
            st.write("No specific warning signs were returned.")

        if urgency == "EMERGENCY":
            st.error(
                "🚨 EMERGENCY-LEVEL OUTPUT: Seek emergency medical help immediately."
            )

    with tabs[5]:
        st.subheader("LangChain implementation evidence")

        st.write("**SystemMessage + HumanMessage + AIMessage**")
        st.caption(
            "The assignment requires all three message types. The demo below invokes "
            "the model and displays the resulting AIMessage."
        )
        if st.button("Run message demo", key="message_demo"):
            try:
                demo_messages = message_demo(
                    llm,
                    "Explain in one short sentence why symptom information should be "
                    "discussed with a healthcare professional.",
                )
                for msg in demo_messages:
                    st.code(
                        f"{msg.__class__.__name__}: {msg.content}",
                        language="text",
                    )
            except Exception as exc:
                st.error(f"Message demo failed: {exc}")

        st.write("**ChatPromptTemplate messages used by the application**")
        chat_messages = build_chat_assessment_messages(inputs)
        for msg in chat_messages:
            st.code(
                f"{msg.__class__.__name__}: {msg.content}",
                language="text",
            )

        st.write("**Structured JSON returned by the assessment chain**")
        st.json(parsed)

    # Required streaming section: uses llm.stream() and st.write_stream().
    st.divider()
    st.subheader("📝 Live patient-friendly guidance")
    st.caption(
        "The narrative below is streamed with LangChain's `llm.stream()` and "
        "displayed using Streamlit's `st.write_stream()`."
    )

    try:
        stream_start = time.perf_counter()
        streamed_text = st.write_stream(
            stream_narrative(
                llm,
                json.dumps(parsed, ensure_ascii=False),
                answer_language,
            )
        )
        stream_elapsed = time.perf_counter() - stream_start
        st.caption(f"Streaming finished in approximately {stream_elapsed:.2f} seconds.")
        st.info(
            "Educational guidance only. This output is not a diagnosis or a "
            "substitute for professional medical care."
        )
    except Exception as exc:
        st.error(f"Streaming failed: {exc}")

# Always-visible footer safety notice.
st.divider()
st.error(
    "MEDICAL SAFETY REMINDER: This educational prototype cannot diagnose illness. "
    "Consult a qualified healthcare professional. Seek emergency help immediately "
    "for urgent or severe symptoms."
)
