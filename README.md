# 🩺 MediGuide AI

**AI-Powered Medical Symptom Assessment and Patient Guidance Assistant**

MediGuide AI is an educational LangChain + Streamlit prototype based directly on the
course assignment requirements. A user enters age, gender, symptoms, duration,
severity, existing conditions, medications, and notes. The application sends the
information through a LangChain `LLMChain` backed by OpenAI and safely renders a
structured JSON assessment.

> **IMPORTANT MEDICAL & SAFETY NOTICE**
>
> This is an educational AI prototype only. It is **NOT** a doctor, licensed
> healthcare professional, professional diagnosis service, emergency service, or
> medical treatment. It must never be used to confirm a diagnosis. For urgent or
> severe symptoms, seek emergency medical help immediately.

## 1. Requirements covered

The project implements the required assignment elements:

- Streamlit UI with `text_input`, `text_area`, `selectbox`, `multiselect`, `slider`,
  and `button`.
- Sidebar with app name, description, safety disclaimer, model configuration,
  caching selection, and language selection.
- OpenAI integration through `ChatOpenAI`.
- Reusable `PromptTemplate`.
- Reusable `ChatPromptTemplate`.
- Explicit `SystemMessage`, `HumanMessage`, and `AIMessage` demonstration.
- Reusable `LLMChain`.
- Exact structured JSON schema.
- Defensive JSON parsing with `try/except`.
- Human-readable streaming using `llm.stream()` and `st.write_stream()`.
- Both `InMemoryCache` and `SQLiteCache`.
- Cache can be disabled.
- Emergency/high urgency warnings.
- No API call when symptoms are empty.
- English and Urdu answer language.
- Modular `src/` backend and `app.py` UI.
- `.env` API-key handling.
- Beginner-friendly comments.

The required project flow is:

```text
Streamlit form
    ↓
build prompt inputs
    ↓
select cache
    ↓
ChatOpenAI + LLMChain
    ↓
structured JSON
    ↓
safe JSON parser
    ↓
results dashboard
    ↓
llm.stream()
    ↓
st.write_stream()
```

## 2. Project structure

```text
medical_ai_assistant/
│
├── app.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
│
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── prompts.py
│   ├── chains.py
│   ├── cache_manager.py
│   └── utils.py
│
└── docs/
    └── Medical_AI_Assignment.pdf
```

## 3. Installation

### Windows PowerShell

Open the project directory:

```powershell
cd medical_ai_assistant
```

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If PowerShell blocks activation, you can run the virtual environment's Python
directly:

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 4. OpenAI API key

Copy:

```text
.env.example
```

to:

```text
.env
```

Then edit `.env`:

```env
OPENAI_API_KEY=sk-your-real-key
OPENAI_MODEL=gpt-4o-mini
OPENAI_TEMPERATURE=0.2
```

**Never commit `.env` to GitHub.** It is already listed in `.gitignore`.

## 5. Run the application

```powershell
streamlit run app.py
```

Then open the local Streamlit URL displayed in the terminal.

## 6. Caching demonstration

The sidebar contains three options.

### InMemoryCache

- Stored in RAM.
- Fastest.
- Lost when the application process stops.
- Best for one session.

### SQLiteCache

- Stored in `mediguide_cache.db`.
- Slightly slower than RAM.
- Survives application restarts.
- Useful for reusing identical model requests across sessions.

### None

Disables caching.

LangChain's global cache is registered once with:

```python
set_llm_cache(...)
```

After registration, LangChain checks the cache automatically before an eligible
model call.

### How to demonstrate caching

1. Select `InMemoryCache`.
2. Submit exactly the same patient form twice.
3. Observe the second request is served from cache rather than requiring a new
   model generation.
4. Repeat using `SQLiteCache`.
5. Stop and restart Streamlit.
6. With the same SQLite cache database still present, repeat the same request.

**Important:** cache keys depend on the model request. Changing patient input,
model, or prompt can produce a different cache entry.

## 7. Structured JSON

The required assessment structure is:

```json
{
  "summary": "",
  "possible_conditions": [
    {
      "name": "",
      "reason": ""
    }
  ],
  "urgency_level": "",
  "recommended_next_steps": [],
  "questions_for_doctor": [],
  "warning_signs": []
}
```

The parser in `src/utils.py`:

1. Removes accidental Markdown JSON fences.
2. Attempts `json.loads()`.
3. Checks that the result is an object.
4. Checks all required fields.
5. Validates urgency as `LOW`, `MEDIUM`, `HIGH`, or `EMERGENCY`.
6. Validates list fields.
7. Returns an error instead of crashing if parsing fails.

## 8. LangChain concepts

### ChatOpenAI

`src/chains.py` creates:

```python
ChatOpenAI(...)
```

using the API key and model from `.env`.

### PromptTemplate

`src/prompts.py` defines a reusable single-string prompt containing:

- age
- gender
- symptoms
- duration
- severity
- existing conditions
- medications
- notes
- language

### ChatPromptTemplate

`src/prompts.py` also defines a System + Human conversation template.

### SystemMessage / HumanMessage / AIMessage

`message_demo()` creates:

```text
SystemMessage
HumanMessage
```

then calls the model and appends the returned:

```text
AIMessage
```

The Streamlit "LangChain details" tab lets you demonstrate this.

### LLMChain

`build_assessment_chain()` creates the reusable assessment chain and
`run_assessment()` executes it.

### Streaming

`stream_narrative()` calls:

```python
llm.stream(...)
```

and yields each non-empty chunk. The Streamlit UI displays those chunks with:

```python
st.write_stream(...)
```

## 9. Testing checklist from the assignment

### Scenario 1 — Mild symptoms

Example:

```text
Age: 25
Symptoms: Runny nose, Sore throat
Duration: 1-3 days
Severity: 2
```

Expected: generally LOW urgency and calm monitoring guidance.

### Scenario 2 — Fever and cough

Example:

```text
Age: 40
Symptoms: Fever, Cough
Duration: 4-7 days
Severity: 6
```

Expected: MEDIUM/HIGH may be returned with advice to seek professional
assessment.

### Scenario 3 — Severe chest symptoms

Example:

```text
Symptoms: Chest pain, Shortness of breath
```

Expected: HIGH/EMERGENCY-type safety guidance and immediate help instruction.

### Scenario 4 — Cache

Submit exactly the same form twice with caching enabled.

Expected: identical cached assessment and reduced repeated model work.

### Scenario 5 — Empty symptoms

Submit without symptoms.

Expected: a local warning and **no API call**.

### Scenario 6 — Urdu

Set:

```text
Answer language = Urdu
```

Expected: guidance narrative is requested in Urdu.

## 10. GitHub submission

Initialize Git:

```powershell
git init
git add .
git commit -m "Initial MediGuide AI assignment"
```

Create a GitHub repository, then connect it:

```powershell
git branch -M main
git remote add origin YOUR_GITHUB_REPOSITORY_URL
git push -u origin main
```

Before pushing, verify `.env` is not staged:

```powershell
git status
```

The repository should contain `.env.example`, but **not** `.env`.

## 11. Demo plan

For a short assignment demonstration:

1. Start `streamlit run app.py`.
2. Point out the prominent medical safety notice.
3. Show the sidebar and cache options.
4. Enter a mild symptom case.
5. Submit and show the structured dashboard.
6. Open "Possible conditions" and explain that these are educational only.
7. Open "LangChain details" and show the message objects and JSON.
8. Show the live streaming narrative.
9. Submit the exact same case again with cache enabled.
10. Demonstrate the empty-symptom validation.
11. Demonstrate an emergency-like scenario and show the prominent urgent-help warning.

## 12. Important academic note

The application is deliberately a **prototype**, not a medical device. The system
prompt, UI warnings, urgency messaging, and output wording are designed to meet
the assignment's explicit safety constraints.

Do not present the application as clinically validated or suitable for real patient
diagnosis/treatment.
