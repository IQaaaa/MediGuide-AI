from src.utils import safe_parse_json

def test_valid_json():
    data, error = safe_parse_json("""
    {
      "summary": "Example",
      "possible_conditions": [{"name": "Example", "reason": "Educational only"}],
      "urgency_level": "LOW",
      "recommended_next_steps": ["Monitor symptoms"],
      "questions_for_doctor": ["What should I watch for?"],
      "warning_signs": ["Severe worsening"]
    }
    """)
    assert error is None
    assert data["urgency_level"] == "LOW"

def test_invalid_json_does_not_crash():
    data, error = safe_parse_json("{not valid json")
    assert data is None
    assert error
