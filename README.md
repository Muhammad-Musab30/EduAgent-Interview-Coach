# EduAgent Interview Coach

**EduAgent Interview Coach** is an adaptive, text-based technical interview practice web application designed for students and junior software developers preparing for Data Structures and Algorithms (DSA) interviews and viva examinations.

The initial version focuses on **Stacks and Queues**, using a closed-loop learning process: **assess, identify a gap, practice the gap, and reassess**.

---

## Features

- **Reviewed Question Bank:** 8–12 reviewed DSA interview questions for Stacks and Queues with explicit concept tags, hints, and follow-up relationships.
- **Consistent 10-Point Scoring Rubric:**
  - Technical Correctness: 0–4
  - Key Concepts: 0–3
  - Reasoning: 0–2
  - Clarity: 0–1
- **Deterministic Adaptive Engine:** Selects targeted follow-ups based on identified gaps (strong responses progress, incomplete answers receive targeted follow-ups, and weak answers receive scaffolded assistance).
- **Session Progress & Mastery Tracking:** Tracks demonstrated concepts, missing concepts, and attempted questions without infinite loops.
- **Actionable Final Report:** Summarizes performance, demonstrated concepts, topics to revisit, and concrete revision recommendations.
- **Reliable Local Offline Evaluation:** Fully functional without cloud credentials or internet access.
- **Alexa+ MCP Agent Skill:** Exposes a self-hosted Model Context Protocol (MCP) server allowing Alexa+ agents to conduct interactive interview prep, query candidate weak spots, and generate revision reports.

---

## Project Structure

```text
eduagent-interview-coach/
├── app.py                     # Streamlit web application & UI
├── question_bank.json         # Reviewed questions, hints, and follow-ups
├── interview_engine.py        # Interview session state & lifecycle coordinator
├── evaluator.py               # 10-point answer evaluator & local fallback
├── adaptive_engine.py         # Deterministic follow-up selection & weakness tracking
├── mcp_server.py              # Alexa+ Model Context Protocol (MCP) server
├── report_generator.py        # Session summary & report generator
├── config.py                  # Configuration loader
├── tests/                     # Automated unit and integration tests (63 tests)
│   ├── test_question_bank.py
│   ├── test_evaluator.py
│   ├── test_adaptive_engine.py
│   ├── test_interview_engine.py
│   ├── test_report_generator.py
│   └── test_mcp_server.py
├── requirements.txt           # Python package dependencies
├── .env.example               # Configuration template
├── .gitignore                 # Version control exclusions
├── EduAgent_Interview_Coach_PRD.md     # Product Requirements Document
├── EduAgent_Interview_Coach_TRD.md     # Technology Requirements Document
├── EduAgent_Interview_Coach_UI_UX.md  # UI/UX Design System Specification
├── steps.md                   # AI Coding Activity & Decision Log
├── FRICTION_LOG.md            # Runtime & integration friction log
└── README.md                  # Project documentation
```

---

## Prerequisites

- **Python:** 3.11, 3.12, or 3.14 (64-bit)
- **Git**
- Modern web browser (Chrome, Edge, Firefox, or Safari)

---

## Installation & Setup

### 1. Clone or Open the Repository
```powershell
cd d:\eduagent-interview-coach
```

### 2. Create and Activate Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

## Running the Application

Launch the Streamlit web application:
```powershell
streamlit run app.py
```
Then open the local URL shown in your terminal (typically `http://localhost:8501`).

---

## Running Automated Tests

Run the Pytest suite:
```powershell
python -m pytest -v
```

---

## Alexa+ MCP Agent Skill (Hackathon Track Integration)

EduAgent provides a self-hosted Model Context Protocol (MCP) server that empowers **Alexa+** assistants to interact with the practice system via standardized agent tools:

### Available MCP Tools
- `get_interview_question`: Retrieves a DSA question with topic and difficulty filters.
- `evaluate_student_answer`: Evaluates a student's spoken/text answer using the 10-point rubric.
- `get_session_weaknesses`: Lists concepts requiring practice based on recent attempts.
- `generate_revision_report`: Generates an actionable summary and study recommendations.

### Running the Alexa+ MCP Server
```powershell
python mcp_server.py
```
Or test via MCP Inspector / Alexa+ Skill developer console.

---

## Development & Decision Log

- Development history, architecture decisions, and test logs are tracked in [`steps.md`](./steps.md).
- Runtime issues, API observations, and workarounds are tracked in [`FRICTION_LOG.md`](./FRICTION_LOG.md).
