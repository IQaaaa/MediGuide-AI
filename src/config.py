"""Application configuration and form options for MediGuide AI."""

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.2"))
CACHE_DB_PATH = str(BASE_DIR / "mediguide_cache.db")

GENDER_OPTIONS = ["Prefer not to say", "Female", "Male", "Non-binary", "Other"]
DURATION_OPTIONS = [
    "Less than 24 hours",
    "1-3 days",
    "4-7 days",
    "1-2 weeks",
    "More than 2 weeks",
    "Recurring / comes and goes",
]
LANGUAGE_OPTIONS = ["English", "Urdu"]

COMMON_SYMPTOMS = [
    "Fever",
    "Cough",
    "Sore throat",
    "Runny nose",
    "Headache",
    "Body aches",
    "Fatigue",
    "Nausea",
    "Vomiting",
    "Diarrhea",
    "Abdominal pain",
    "Dizziness",
    "Skin rash",
    "Back pain",
    "Chest pain",
    "Shortness of breath",
    "Other",
]

URGENCY_LEVELS = ["LOW", "MEDIUM", "HIGH", "EMERGENCY"]

MEDICAL_DISCLAIMER = (
    "Educational AI prototype only. MediGuide AI is NOT a doctor and is not a "
    "replacement for a licensed healthcare professional, professional diagnosis, "
    "emergency service, or medical treatment. It must not be used to confirm a "
    "diagnosis. For urgent or severe symptoms, seek emergency medical help immediately."
)
