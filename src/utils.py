"""Validation, safe JSON parsing and display helpers."""

import json
import re
from typing import Any, Dict, Tuple

from .config import URGENCY_LEVELS


def clean_json_text(raw_text: str) -> str:
    """Remove common Markdown fences or accidental surrounding text."""
    text = (raw_text or "").strip()

    text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s*```$", "", text)

    # If the model added prose around an otherwise valid JSON object, isolate the
    # outermost object. This is intentionally conservative.
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        text = text[start : end + 1]

    return text.strip()


def safe_parse_json(raw_text: str) -> Tuple[Dict[str, Any] | None, str | None]:
    """Parse model JSON without allowing malformed JSON to crash the app."""
    cleaned = clean_json_text(raw_text)

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        return None, f"Invalid JSON returned by the model: {exc}"

    if not isinstance(data, dict):
        return None, "The model returned JSON, but it was not a JSON object."

    required = {
        "summary",
        "possible_conditions",
        "urgency_level",
        "recommended_next_steps",
        "questions_for_doctor",
        "warning_signs",
    }
    missing = required - set(data.keys())
    if missing:
        return None, f"JSON is missing required fields: {', '.join(sorted(missing))}"

    urgency = str(data.get("urgency_level", "")).upper().strip()
    if urgency not in URGENCY_LEVELS:
        return None, (
            "The model returned an unsupported urgency level. "
            "Expected LOW, MEDIUM, HIGH, or EMERGENCY."
        )

    # Normalize list fields so the renderer can safely iterate.
    for key in [
        "possible_conditions",
        "recommended_next_steps",
        "questions_for_doctor",
        "warning_signs",
    ]:
        if not isinstance(data[key], list):
            return None, f"The JSON field '{key}' must be a list."

    data["urgency_level"] = urgency
    return data, None


def urgency_message(level: str) -> str:
    level = level.upper()
    if level == "EMERGENCY":
        return "Seek emergency medical help immediately."
    if level == "HIGH":
        return "Contact a qualified healthcare professional promptly."
    if level == "MEDIUM":
        return "Consider arranging a professional medical assessment soon."
    return "Monitor symptoms and consider professional advice if they persist or worsen."


def format_patient_summary(inputs: Dict[str, Any]) -> str:
    """Create a safe, local summary without calling the model."""
    return (
        f"Age: {inputs['age']} | Gender: {inputs['gender']} | "
        f"Duration: {inputs['duration']} | Severity: {inputs['severity']}/10"
    )
