"""Reusable PromptTemplate and ChatPromptTemplate definitions."""

from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

JSON_SCHEMA = """
{{
  "summary": "string",
  "possible_conditions": [
    {{
      "name": "string",
      "reason": "string"
    }}
  ],
  "urgency_level": "LOW | MEDIUM | HIGH | EMERGENCY",
  "recommended_next_steps": ["string"],
  "questions_for_doctor": ["string"],
  "warning_signs": ["string"]
}}
"""

SYSTEM_PROMPT = """
You are MediGuide AI, an educational medical symptom assessment assistant.

NON-NEGOTIABLE SAFETY RULES:
1. You are not a doctor and must never claim to be one.
2. Never provide a confirmed diagnosis. Possible conditions are for education only.
3. Do not tell the user that a condition is definitely present.
4. Encourage consultation with a qualified healthcare professional.
5. If symptoms could represent an emergency, use EMERGENCY or HIGH and clearly tell
   the user to seek emergency medical help immediately.
6. Do not recommend stopping, starting, or changing prescription medication.
7. Be calm, clear, non-judgmental, and avoid unnecessary alarm.
8. Use only the information supplied by the user; do not invent patient history.
9. The urgency level is a safety-oriented triage suggestion, not a diagnosis.
10. Return ONLY valid JSON for assessment requests. No Markdown fences and no commentary.

The JSON object MUST exactly follow this structure:
""" + JSON_SCHEMA

# Required single-string PromptTemplate.
ASSESSMENT_PROMPT = PromptTemplate(
    input_variables=[
        "age",
        "gender",
        "symptoms",
        "duration",
        "severity",
        "conditions",
        "medications",
        "notes",
        "language",
    ],
    template=(
        "Assess the following patient information for educational guidance.\n\n"
        "Age: {age}\n"
        "Gender: {gender}\n"
        "Selected symptoms: {symptoms}\n"
        "Duration: {duration}\n"
        "Severity (1-10): {severity}\n"
        "Existing medical conditions: {conditions}\n"
        "Current medications: {medications}\n"
        "Additional notes: {notes}\n"
        "Answer language: {language}\n\n"
        "Return ONLY the exact JSON schema specified in the system instructions."
    ),
)

# Required System + Human ChatPromptTemplate.
ASSESSMENT_CHAT_TEMPLATE = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        (
            "human",
            "Patient information:\n"
            "Age: {age}\n"
            "Gender: {gender}\n"
            "Selected symptoms: {symptoms}\n"
            "Duration: {duration}\n"
            "Severity (1-10): {severity}\n"
            "Existing medical conditions: {conditions}\n"
            "Current medications: {medications}\n"
            "Additional notes: {notes}\n"
            "Answer language: {language}\n\n"
            "Return ONLY valid JSON matching the exact required schema.",
        ),
    ]
)

NARRATIVE_CHAT_TEMPLATE = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are generating a human-readable explanation of an already-produced
educational medical assessment.

Safety rules:
- Do not present a confirmed diagnosis.
- Make clear that possible conditions are educational possibilities only.
- Encourage consultation with a qualified healthcare professional.
- If urgency is HIGH or EMERGENCY, clearly advise urgent/emergency medical help.
- Do not advise changing prescription medication.
- Be concise and understandable.
- Respond in the requested language.
""",
        ),
        (
            "human",
            """
Write a short patient-friendly guidance narrative from this assessment:

{assessment_json}

Requested language: {language}

Do not add a diagnosis or medical certainty. End by reminding the user that this
is educational guidance and not a substitute for professional medical care.
""",
        ),
    ]
)

# A small message demo explicitly using SystemMessage, HumanMessage and AIMessage.
MESSAGE_DEMO_SYSTEM = (
    "You are a safety-first educational assistant. Never claim a confirmed diagnosis."
)
