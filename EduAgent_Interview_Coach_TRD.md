# EduAgent Interview Coach

## Technology Requirements Document (TRD)

**Document version:** 1.0
**Date:** 21 October 2026
**Status:** Initial technical baseline
**Related document:** `EduAgent_Interview_Coach_PRD.md`

---

## 1. Purpose

This document defines the technical architecture, programming languages, packages, libraries, data formats, interfaces, security measures, testing strategy, and implementation decisions for EduAgent Interview Coach.

It serves as the technical implementation guide for building a working hackathon prototype with a small team or as a solo beginner developer.

### 1.1 Product scope

EduAgent Interview Coach is a text-based interview practice web application. The first version focuses exclusively on **Data Structures and Algorithms (DSA): Stacks and Queues**.

The application asks questions, evaluates typed answers, identifies missing concepts, selects targeted follow-up questions, tracks progress, and generates a final performance report.

### 1.2 Core technical principles

1. Keep the application small and modular.
2. Make core interview functionality work without an external AI service.
3. Use explicitly reviewed questions instead of unrestricted question generation.
4. Keep adaptive question selection deterministic and testable.
5. Provide a self-hosted Model Context Protocol (MCP) server for Alexa+ Agent Skills.
6. Support offline-first local evaluation with structured validation.
7. Do not claim that simulated agent actions are actual external tool calls.
8. Avoid unnecessary infrastructure, dependencies, and features.

---

## 2. System Requirements

### 2.1 Functional requirements

The system must:

- Start and run a text-only interview session.
- Present questions from a local question bank.
- Accept a student's typed answer.
- Evaluate the answer using a defined scoring rubric.
- Identify correct points, missing concepts, and possible misconceptions.
- Choose a follow-up question based on the evaluation.
- Track attempted questions and demonstrated concepts.
- Allow the student to request a hint.
- Generate a final report with scores and recommendations.
- Work entirely offline without external credentials or network access.
- Expose standardized MCP tools for Alexa+ Agent Skills.
- Recover gracefully from malformed inputs or service failures.

### 2.2 Non-functional requirements

| Requirement     | Technical target                                                    |
| --------------- | ------------------------------------------------------------------- |
| Reliability     | Core interview loop works without network access after installation |
| Maintainability | Separate UI, interview flow, evaluation, and adaptation modules     |
| Testability     | Core logic can be tested without launching Streamlit                |
| Security        | No API keys committed to source control                             |
| Explainability  | Show why a follow-up question was selected                          |
| Performance     | Avoid unnecessary external calls and repeated evaluations           |
| Portability     | Run on a supported Windows, Linux, or macOS Python environment      |
| Usability       | Clear question progress, feedback, hints, and completion state      |

---

## 3. Technology Stack

### 3.1 Selected technologies

| Layer                | Technology                                                   | Purpose                                 |
| -------------------- | ------------------------------------------------------------ | --------------------------------------- |
| Programming language | Python 3.11, 3.12, or 3.14                                   | Main application language               |
| User interface       | Streamlit                                                    | Interactive web application             |
| Question storage     | JSON                                                         | Local, version-controlled question bank |
| Application state    | Streamlit Session State                                      | Current session and progress            |
| Evaluation           | Python deterministic rules + concept synonym clusters        | Answer assessment                       |
| Agent Integration    | Model Context Protocol (MCP standard)                        | Alexa+ Agent Skill interface            |
| Configuration        | Environment variables; `python-dotenv` for local development | Manage configuration and ports          |
| Validation           | Python standard library                                      | Validate data and tool schemas          |
| Unit testing         | Pytest                                                       | Test core application behavior          |
| Version control      | Git                                                          | Track code and configuration changes    |
| Documentation        | Markdown                                                     | PRD, TRD, README, friction log          |

### 3.2 Explicitly excluded from version 1

The following are not part of the initial implementation:

- React, Next.js, or a separate JavaScript frontend.
- A separate FastAPI backend (Streamlit + standard MCP server handles both UI and agent access).
- PostgreSQL, MongoDB, or Redis.
- User accounts and authentication.
- Voice recognition, speech synthesis, or live audio.
- Resume parsing and coding-execution environments.
- Training or fine-tuning a custom model.
- Kubernetes, Docker-based orchestration, or microservices.
- Mandatory cloud hosting.

These exclusions keep the application achievable and reduce the number of failure points during the hackathon.

---

## 4. System Architecture

### 4.1 High-level architecture

```text
                 STUDENT                        ALEXA+ AGENT
                    |                                 |
                    v                                 v
          +---------------------+           +---------------------+
          | Streamlit UI        |           | Alexa+ MCP Server   |
          | app.py              |           | mcp_server.py       |
          +---------------------+           +---------------------+
                    |                                 |
                    +---------------+-----------------+
                                    |
                                    v
                          +---------------------+
                          | Interview Engine    |
                          | Session lifecycle   |
                          +---------------------+
                                    |
                          +---------+----------+
                          |                    |
                          v                    v
                +------------------+  +------------------+
                | Question Bank    |  | Evaluator        |
                | JSON file        |  | 10-point rubric  |
                | Reviewed prompts |  | Local Evaluator  |
                +------------------+  +------------------+
                          |                    |
                          |                    v
                          |          +------------------+
                          |          | Output Validator |
                          |          | Schema + ranges  |
          |          +------------------+
          |                    |
          +----------+---------+
                     |
                     v
          +---------------------+
          | Adaptive Engine     |
          | Rules + concept map |
          +---------------------+
                     |
                     v
          +---------------------+
          | Session Report      |
          | Scores and feedback |
          +---------------------+
```

### 4.2 Architecture explanation

**Streamlit UI:** Displays the interview, collects typed answers, displays feedback, and manages user interactions.

**Interview Engine:** Coordinates the session lifecycle, question presentation, answer submission, evaluation, and completion.

**Question Bank:** Supplies reviewed questions and their concept tags, difficulty, hints, and follow-up relationships.

**Evaluator:** Scores the submitted answer using the local evaluator or the configured AI provider.

**Output Validator:** Checks that an evaluation contains the required fields, valid score ranges, and acceptable values.

**Adaptive Engine:** Applies deterministic rules to select the next question based on the evaluation and previous attempts.

**Session Report:** Summarizes the session's performance, demonstrated concepts, unresolved weaknesses, and recommendations.

### 4.3 Architecture decision: one application, modular files

Use a **modular monolithic architecture**.

Every module runs inside the same Python application. Modules have separate responsibilities, but no network APIs are required between them.

This is preferable to a separate frontend and backend because it reduces deployment complexity, dependency management, and debugging effort.

---

## 5. Project Structure

Use the following directory structure:

```text
eduagent-interview-coach/
│
├── app.py
├── question_bank.json
├── interview_engine.py
├── evaluator.py
├── adaptive_engine.py
├── mcp_server.py
├── report_generator.py
├── config.py
│
├── tests/
│   ├── test_question_bank.py
│   ├── test_evaluator.py
│   ├── test_adaptive_engine.py
│   └── test_interview_engine.py
│
├── docs/
│   └── architecture.md
│
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── EduAgent_Interview_Coach_PRD.md
├── EduAgent_Interview_Coach_TRD.md
└── FRICTION_LOG.md
```

### 5.1 Module responsibilities

| File                   | Responsibility                                                              |
| ---------------------- | --------------------------------------------------------------------------- |
| `app.py`               | Streamlit screens, inputs, buttons, feedback, and session-state integration |
| `question_bank.json`   | Reviewed questions, concepts, hints, and follow-up links                    |
| `interview_engine.py`  | Coordinates session creation, submission, progression, and completion       |
| `evaluator.py`         | Evaluation interface, local evaluator, and result validation                |
| `adaptive_engine.py`   | Deterministic follow-up selection and weakness tracking                     |
| `bedrock_client.py`    | Optional AWS Bedrock Runtime integration                                    |
| `report_generator.py`  | Creates the final session report                                            |
| `config.py`            | Loads configuration and validates environment settings                      |
| `tests/`               | Automated tests for core functionality                                      |
| `docs/architecture.md` | Optional detailed architecture notes                                        |

**Implementation rule:** Keep Streamlit-specific code in `app.py`. Core scoring and adaptation functions should accept ordinary Python data and return ordinary Python data so they can be tested independently.

---

## 6. Runtime and Package Requirements

### 6.1 Python version

Use Python 3.11, 3.12, or 3.14 for implementation and testing.

Select one Python version for development and testing, then use that same version for the final demo. Avoid changing the Python version late in development.

### 6.2 Required packages

Maintain the following initial `requirements.txt`:

```text
streamlit>=1.40,<2.0
pytest>=8.0,<10.0
```

### 6.3 Optional packages

Add these only when the relevant feature is implemented:

```text
mcp>=1.0.0,<2.0.0
python-dotenv>=1.0,<2.0
```

- `mcp` is used for running the standard Model Context Protocol server exposing Alexa+ Agent Skills.
- `python-dotenv` loads local `.env` configuration during development. It is not necessary in a deployment environment that already supplies environment variables.

These are compatibility ranges, not a verified lockfile. After the first successful build, test the chosen versions and pin the exact versions in a lockfile or the final requirements file before submission.

### 6.4 Standard-library modules

Prefer Python's standard library for small tasks:

| Module          | Use                                     |
| --------------- | --------------------------------------- |
| `json`          | Read and parse the question bank        |
| `os`            | Access environment variables            |
| `typing`        | Type annotations                        |
| `dataclasses`   | Optional structured result objects      |
| `enum`          | Evaluation status and difficulty values |
| `pathlib`       | Portable file paths                     |
| `logging`       | Application diagnostics                 |
| `datetime`      | Session timestamps                      |
| `unittest.mock` | Mock AI calls during testing            |

Do not add a package simply because a task can be performed with it. Add dependencies only when they provide clear value.

---

## 7. Question Bank Specification

### 7.1 Storage decision

Store reviewed questions in `question_bank.json`.

The question bank must be version-controlled and loadable without a database or internet connection.

### 7.2 Required question fields

Each question should contain:

- `id`: Unique identifier.
- `topic`: Topic name.
- `concepts`: Concepts assessed by the question.
- `difficulty`: `easy`, `medium`, or `hard`.
- `question`: The prompt shown to the student.
- `expected_points`: Essential ideas an answer should cover.
- `critical_misconceptions`: Errors that require additional teaching.
- `hint`: A short hint.
- `follow_up_ids`: IDs of appropriate follow-up questions.
- `fallback_follow_up_id`: A safe default follow-up, if applicable.

### 7.3 Example question

```json
{
  "id": "stack_001",
  "topic": "Stacks",
  "concepts": ["LIFO", "push", "pop"],
  "difficulty": "easy",
  "question": "Explain the LIFO principle of a stack and describe push and pop operations.",
  "expected_points": [
    "LIFO means Last In, First Out",
    "Push adds an element to the top",
    "Pop removes the top element"
  ],
  "critical_misconceptions": [
    "Pop removes the oldest element"
  ],
  "hint": "Think about a stack of plates.",
  "follow_up_ids": ["stack_002", "stack_003"],
  "fallback_follow_up_id": "stack_002"
}
```

This is a format example; the final question bank must be reviewed and tested before the demo.

### 7.4 Question-bank validation

At application startup:

1. Verify that the file exists and contains valid JSON.
2. Verify that every question has the required fields.
3. Verify that IDs are unique.
4. Verify that referenced follow-up IDs exist.
5. Verify that difficulty values are allowed.
6. Verify that concepts and expected points are non-empty.
7. Display a useful error if validation fails.

Do not silently skip malformed questions or replace a missing question bank with fabricated data.

---

## 8. Evaluation Architecture

### 8.1 Evaluation providers

The evaluator should expose one consistent interface regardless of provider.

```python
def evaluate_answer(question, answer):
    ...
```

It returns a validated evaluation result.

Internally, the application uses:

- `LocalEvaluator`: Deterministic, offline 10-point rubric evaluation using conceptual synonym clusters and misconception detection.
- Standardized evaluation interface callable directly by the Streamlit UI or externally via the Alexa+ MCP Server (`evaluate_student_answer` tool).

Both invocation paths return the identical validated result structure.

### 8.2 Evaluation result schema

```json
{
  "score": 7,
  "score_breakdown": {
    "technical_correctness": 3,
    "key_concepts": 2,
    "reasoning": 1,
    "clarity": 1
  },
  "correct_points": [
    "Correctly identified LIFO"
  ],
  "missing_concepts": [
    "Did not explain pop"
  ],
  "misconceptions": [],
  "feedback": "Your definition is correct, but explain both push and pop operations.",
  "confidence": "high",
  "recommended_action": "targeted_follow_up",
  "evaluation_provider": "local"
}
```

The schema is enforced by `validate_evaluation_result(result)`. The application validates every field before using the result.

### 8.3 Scoring rubric

Use the PRD's ten-point rubric:

| Criterion             | Maximum score |
| --------------------- | ------------: |
| Technical correctness |             4 |
| Key concepts          |             3 |
| Reasoning             |             2 |
| Clarity               |             1 |
| **Total**             |        **10** |

The final score must be an integer from 0 to 10.

The rubric provides practice feedback, not a validated measure of real interview performance. The application should not imply that its scores are objectively accurate or equivalent to an employer's assessment.

### 8.4 Local evaluator

The local evaluator must:

- Work without credentials or internet access.
- Use reviewed question metadata, expected concepts, and critical misconceptions.
- Identify clearly missing essential points and misconceptions.
- Produce consistent, deterministic results for identical inputs.
- Avoid claiming semantic understanding it cannot reliably provide.

A local keyword or phrase matcher is an offline assessment tool. It may miss certain paraphrases or nuanced explanations. Communicate this transparently in the interface and final report.

### 8.5 MCP Agent Tool Interface

When invoked by an Alexa+ agent or external client, the evaluation tool receives:

- The question ID or question text.
- The student's answer.
- Optional evaluation mode parameter.

It validates the input, runs the evaluator, verifies the output schema, and returns structured JSON conforming to the MCP tool specification.

The external agent must not be allowed to choose arbitrary question IDs or directly alter internal session state without passing through the Interview Engine.

### 8.6 Validation and fallback

Before an evaluation is accepted, validate:

- Required keys are present.
- `score` is an integer from 0 to 10.
- Feedback fields have the expected types.
- `confidence` uses an allowed value.
- `recommended_action` is one of the supported actions.
- Text and list sizes are within reasonable limits.

If AI evaluation fails, returns malformed data, times out, or exceeds the configured retry limit:

1. Record a diagnostic event without exposing secrets.
2. Run the local evaluator if the answer can be evaluated locally.
3. Clearly indicate that fallback evaluation was used.
4. Continue the interview if safe.
5. Never present an unvalidated model response as a trusted result.

---

## 9. Adaptive Engine Specification

### 9.1 Decision ownership

The adaptive engine is deterministic application code. It uses the evaluation result, question metadata, attempted-question history, and demonstrated concepts.

The AI evaluator supplies evidence for the decision, but does not control the decision process.

### 9.2 Decision rules

| Evaluation result                       | Application action                                                        |
| --------------------------------------- | ------------------------------------------------------------------------- |
| Score 8–10, no critical misconception   | Mark applicable concepts as demonstrated and select a next-level question |
| Score 5–7 or essential concepts missing | Select a targeted follow-up covering the missing concepts                 |
| Score 0–4 or a critical misconception   | Show a hint and select a simpler scaffolded follow-up                     |
| No eligible follow-up exists            | Select an appropriate unattempted question or end the session             |
| Evaluation fails                        | Use the local fallback and apply the same validated decision rules        |

A high score alone must not mark a concept as demonstrated if the evaluation identifies a critical misconception.

### 9.3 Selection constraints

The adaptive engine must:

- Select only IDs that exist in the question bank.
- Avoid asking the exact same question repeatedly within a session, except when an explicit retry feature is introduced.
- Prefer questions that target unresolved concepts.
- Avoid selecting a question already attempted when a suitable alternative exists.
- Avoid infinite loops if follow-up links form a cycle.
- Have a defined end condition when no suitable questions remain.

### 9.4 Explainability

For each adaptive decision, keep an internal reason such as:

- `missing_concept`
- `critical_misconception`
- `mastery_demonstrated`
- `fallback_after_evaluation_error`
- `no_eligible_follow_up`

The UI can translate this into a student-friendly message such as: “Next question selected because your answer did not explain the pop operation.”

---

## 10. Interview Session and State Management

### 10.1 State storage decision

Use `st.session_state` for the active interview session.

Do not introduce a database for the first version.

### 10.2 Suggested session state

```python
{
    "session_id": "...",
    "current_question_id": "stack_001",
    "attempts": [],
    "demonstrated_concepts": [],
    "unresolved_concepts": [],
    "asked_question_ids": [],
    "evaluation_provider": "local",
    "session_status": "in_progress"
}
```

This illustrates the logical fields; the implementation may use dataclasses or another simple Python structure.

### 10.3 State rules

- Initialize state only when a new session starts.
- Preserve state across Streamlit reruns.
- Record an answer only once per submission.
- Prevent double-submission from creating duplicate attempts.
- Reset only when the student explicitly starts a new session.
- Show a clear completion state when the interview ends.

**Limitation:** Session state is not permanent storage. It may be lost when the browser session or server process is reset. Persistent accounts, history, and cross-device synchronization are outside version 1.

---

## 11. Alexa+ MCP Server Architecture (Model Context Protocol)

### 11.1 Purpose and Hackathon Track Alignment

In alignment with the "Build, Ship, Shape" Amazon Developer Hackathon primary track: **Alexa+ (including Model Context Protocol / MCP Agent Skills)**, EduAgent Interview Coach provides a self-hosted Model Context Protocol server (`mcp_server.py`).

This architecture allows Alexa+ assistants and autonomous agents to conduct technical interview preparation, dynamically evaluate candidate explanations using the locked 10-point rubric, inspect candidate knowledge gaps, and generate revision reports.

### 11.2 MCP Transport and Configuration

The server supports two standard MCP transports:
- **`stdio` (Standard I/O):** For direct integration with local agent runtimes and command-line MCP clients.
- **`sse` (Server-Sent Events / HTTP):** For network-based communication with Alexa+ agent skills and developer test harnesses (configured via `MCP_SERVER_HOST` and `MCP_SERVER_PORT`).

Example `.env.example`:

```text
EVALUATION_MODE=local
MCP_SERVER_HOST=127.0.0.1
MCP_SERVER_PORT=8000
MCP_TRANSPORT=stdio
```

### 11.3 Exposed MCP Tool Specifications

The MCP server exposes four focused, high-value tools conforming to the official Model Context Protocol JSON schema:

#### Tool 1: `get_interview_question`
- **Description:** Retrieve an interview question from the reviewed Stacks and Queues question bank.
- **Input schema:**
  - `topic` (string, optional): `"Stacks"` or `"Queues"`.
  - `difficulty` (string, optional): `"easy"`, `"medium"`, or `"hard"`.
  - `question_id` (string, optional): Specific ID (e.g., `"stack_001"`).
- **Output:** JSON containing `id`, `topic`, `difficulty`, `question`, and `hint`.

#### Tool 2: `evaluate_student_answer`
- **Description:** Evaluate a candidate's written technical explanation against the 10-point rubric and identify missing concepts and critical misconceptions.
- **Input schema:**
  - `question_id` (string, required): The ID of the question being answered.
  - `student_answer` (string, required): The candidate's explanation.
- **Output:** Validated evaluation result containing `score` (0–10), `score_breakdown`, `correct_points`, `missing_concepts`, `misconceptions`, `feedback`, `recommended_action`, and `confidence`.

#### Tool 3: `get_session_weaknesses`
- **Description:** Retrieve the candidate's tracked concept gaps, unresolved topics, and identified misconceptions from the active interview session.
- **Input schema:** None.
- **Output:** List of unresolved concept tags and misconception details.

#### Tool 4: `generate_revision_report`
- **Description:** Generate a comprehensive post-interview performance report and prioritized study recommendations.
- **Input schema:** None.
- **Output:** Complete session report including aggregate score, attempted questions, demonstrated concepts, unresolved gaps, and prioritized study recommendations.

### 11.4 Security and Validation Rules

- **Strict Schema Enforcement:** Every tool argument is validated against its schema before processing.
- **Sandboxed Execution:** The MCP server strictly exposes domain-specific interview tools; no arbitrary file access, shell execution, or unrestricted networking is permitted.
- **No Credential Leakage:** Sensitive environment variables or system paths are never exposed in tool outputs or error messages.

---

## 12. Offline-First Design and Agent Transparency

### 12.1 Offline-First Principle

EduAgent is built offline-first:
- The Streamlit web interface (`app.py`), question bank (`question_bank.json`), and evaluation engine (`evaluator.py`) operate without any external network dependency.
- The Alexa+ MCP Server uses the same core domain logic, ensuring that agent capabilities are 100% testable and operable locally.

### 12.2 Transparency and Truthfulness

- **Never fake tool execution:** When testing or demonstrating the MCP integration, calls must execute real functions against the question bank and evaluator.
- **Clear Mode Indicators:** The UI and report generator clearly display the active operational mode (`"local"`).
- **Explainable Decisions:** Every adaptive recommendation provides a beginner-friendly explanation explaining why the action was chosen.

---

## 13. User Interface Requirements

### 13.1 Required screens

**A. Start screen**

- Product title and purpose.
- Topic and role: DSA — Stacks and Queues; Junior Software Developer.
- Evaluation mode indicator.
- Start interview button.

**B. Interview screen**

- Current question and difficulty.
- Progress indicator.
- Text input for the answer.
- Submit answer and hint controls.
- Clear submission and loading states.

**C. Feedback screen**

- Score out of 10.
- Correct points.
- Missing concepts.
- Possible misconceptions.
- Actionable feedback.
- Explanation of the next-question choice.

**D. Final report**

- Overall score and number of attempts.
- Demonstrated concepts.
- Concepts that need more practice.
- Recommended next steps.
- Evaluation-mode disclosure and relevant limitations.

### 13.2 UI behavior

- Keep navigation simple.
- Preserve typed answers appropriately during reruns.
- Disable repeated submissions while evaluation is in progress.
- Show a clear error message when a question cannot be loaded.
- Make hints optional and accessible.
- Do not display raw secrets, internal credentials, or unnecessary stack traces.
- Label simulated agent actions as simulated.

---

## 14. Data Handling and Privacy

### 14.1 Initial data policy

Version 1 does not require user accounts or a central database. Session data is held in application memory.

### 14.2 External evaluation disclosure

If Bedrock is enabled, the student's answer and necessary question context are sent to the configured AWS service for evaluation.

The interface and README should explain this behavior and identify the local evaluation option.

### 14.3 Logging policy

Logs may contain:

- Timestamp.
- Event type.
- Evaluation provider.
- Success or failure status.
- Error category.
- Latency measurement, if implemented.

Do not log:

- AWS secrets or access tokens.
- Environment-variable dumps.
- Full credentials or authorization headers.
- Student answers by default.

If diagnostic answer logging is temporarily required, make it explicit, minimize the data, and remove it from the final default configuration.

---

## 15. Error Handling

| Failure                      | Required behavior                                           |
| ---------------------------- | ----------------------------------------------------------- |
| Question bank missing        | Display a clear startup error                               |
| Invalid question JSON        | Stop unsafe question loading and report the problem         |
| Invalid follow-up reference  | Fail validation before the session starts                   |
| Empty answer                 | Request an answer or provide guidance                       |
| MCP client disconnect        | Gracefully close connection without stopping server         |
| Invalid MCP tool arguments   | Return structured JSON-RPC error schema                     |
| Invalid evaluation result    | Reject it and flag schema failure                           |
| Duplicate submission         | Avoid creating a duplicate attempt                          |
| No eligible follow-up        | Select a valid remaining question or finish                 |
| Session state missing        | Offer a safe restart                                        |
| Unexpected application error | Show a concise user-facing message and log safe diagnostics |

Errors must not cause an infinite loop or silently create unsupported scores.

---

## 16. Testing Strategy

### 16.1 Unit tests

**Question bank tests**

- Valid file loads.
- Duplicate IDs are rejected.
- Missing fields are rejected.
- Invalid follow-up IDs are rejected.

**Evaluator tests**

- Scores remain within 0–10.
- Required result fields are present.
- Malformed evaluation results are rejected.
- Local evaluation works offline without credentials.
- Critical misconceptions cap score and recommend hint scaffolding.

**Adaptive engine tests**

- Strong answers move to appropriate questions.
- Missing concepts trigger targeted follow-ups.
- Weak answers trigger scaffolded follow-ups.
- Repeated-question loops are prevented.
- The engine handles an exhausted question bank.

**Interview engine tests**

- A session starts correctly.
- An answer is recorded once.
- A validated evaluation updates progress.
- The session ends when no valid questions remain.
- Multiple submissions are deduplicated.

### 16.2 Integration tests

- Run the full interview with local evaluation.
- Run the interface with valid and invalid question-bank data.
- Test Alexa+ MCP server tools (`get_interview_question`, `evaluate_student_answer`, `get_session_weaknesses`, `generate_revision_report`) over stdio transport.

Automated tests must run locally and deterministically.

### 16.3 Manual acceptance test

A complete manual test should demonstrate:

1. Start a new interview.
2. Answer a question correctly.
3. Answer a question with a missing concept.
4. Receive a relevant follow-up.
5. Trigger the hint flow.
6. Complete the interview.
7. View the final report.
8. Repeat the flow with local evaluation and no AWS configuration.

---

## 17. Development and Execution

### 17.1 Local setup

Create and activate a virtual environment.

**Windows PowerShell**

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

**Linux or macOS**

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If the chosen Python version is not installed, install a supported version before creating the environment.

### 17.2 Run tests

```bash
python -m pytest -q
```

### 17.3 Run the application

```bash
streamlit run app.py
```

### 17.4 Version control

The `.gitignore` file must exclude at least:

```gitignore
.venv/
__pycache__/
.pytest_cache/
.env
*.pyc
```

Keep `.env.example` in the repository, but never commit `.env` or real AWS credentials.

---

## 18. Deployment and Demonstration

### 18.1 Minimum deployment requirement

The application must run locally with the documented setup commands. Public deployment is optional unless required by the final hackathon submission rules.

### 18.2 Deployment constraints

Before using a hosted environment:

- Confirm the hosting platform supports the selected Python version.
- Configure secrets through the platform's secure configuration mechanism.
- Confirm AWS Region, IAM permissions, and model access.
- Avoid assuming that local AWS credentials exist in the hosted environment.
- Test local evaluation even when deployed.
- Confirm whether the session-state behavior is suitable for the chosen hosting setup.

### 18.3 Demo preparation

The demo should use a known set of test questions and expected outcomes. Prepare both the Streamlit web application demonstration and the Alexa+ MCP Server tool interactions (using a local inspector or stdio client).

Never fake a successful agent call or present mocked output as a live response.

---

## 19. Technical Decision Register

| ID    | Decision                        | Rationale                                                                    | Revisit when                                                    |
| ----- | ------------------------------- | ---------------------------------------------------------------------------- | --------------------------------------------------------------- |
| TD-01 | Python                          | Matches the developer's current learning path and supports rapid prototyping | Performance or platform constraints emerge                      |
| TD-02 | Streamlit                       | Minimizes frontend implementation; provides rapid feedback                   | A separate frontend becomes necessary                           |
| TD-03 | Modular monolith                | Easier to build, test, and debug than distributed services                   | The product grows substantially                                 |
| TD-04 | JSON question bank              | Simple, reviewable, offline-friendly data source                             | Questions require persistent editing or concurrent management   |
| TD-05 | Deterministic adaptive engine   | Predictable behavior, transparent explanations, and testability              | A measured improvement justifies a different approach           |
| TD-06 | Local evaluator fallback        | Keeps the core experience available 100% offline without credentials         | Better offline semantic evaluation becomes necessary            |
| TD-07 | Alexa+ MCP Server integration   | Realigns project directly with "Build, Ship, Shape" hackathon track          | Hackathon track or criteria change                              |
| TD-08 | Streamlit session state         | Sufficient for a single-session prototype                                    | Persistent history or accounts become required                  |
| TD-09 | No database in version 1        | Avoids setup and maintenance overhead                                        | Persistence becomes a product requirement                       |
| TD-10 | MCP Standard Tools              | Exposes domain functions via open standard for Alexa+ agents                 | Alternative agent communication protocols emerge                |
| TD-11 | Pytest for automated tests      | Simple, widely used Python test framework                                    | A broader testing architecture is needed                        |
| TD-12 | Environment-based configuration | Keeps secrets and server port configs manageable                             | Deployment requires a managed secrets service                   |

---

## 20. Implementation Order

Build in the following order. Do not start all modules at once.

1. **Project setup:** Create the virtual environment, dependencies, repository, and file structure.
2. **Question bank:** Write and validate 8–12 reviewed questions (`question_bank.json`).
3. **Local evaluator:** Implement the 10-point rubric and validated evaluation result (`evaluator.py`).
4. **Adaptive engine:** Implement deterministic follow-up selection and concept tracking (`adaptive_engine.py`).
5. **Interview engine:** Connect questions, answers, evaluation, and progression (`interview_engine.py`).
6. **Report generator:** Create comprehensive session report (`report_generator.py`).
7. **Streamlit UI:** Build the start, interview, feedback, and report screens (`app.py`).
8. **Alexa+ MCP Server:** Expose standardized MCP interview tools for Alexa+ agents (`mcp_server.py`).
9. **Automated tests:** Verify complete test suite across all modules (`tests/`).
10. **Documentation & QA:** Verify README, TRD, and factual friction log.

The application should remain runnable at every major stage.

---

## 21. Definition of Technical Completion

The technical implementation is ready for the final demo when:

- [ ] The documented environment setup works cleanly.
- [ ] The question bank loads and passes validation.
- [ ] The complete interview flow works in local mode.
- [ ] Evaluation results are validated before use.
- [ ] Adaptive follow-ups match the defined rules.
- [ ] The application prevents invalid question IDs and repeated-question loops.
- [ ] The final report is generated correctly.
- [ ] Automated tests pass across all components.
- [ ] Alexa+ MCP Server exposes tested tools over stdio/SSE.
- [ ] No real secrets are committed to the repository.
- [ ] README instructions reproduce the local demo.
- [ ] The friction log records actual observed problems rather than invented ones.
- [ ] Any simulated functionality is clearly identified as simulated.

---

## 22. Open Decisions Before Final Submission

These items should be verified rather than assumed:

1. **Hackathon rules:** Confirm the current eligibility, deadline, and deliverables for the "Build, Ship, Shape" Alexa+ track.
2. **Hosting:** Decide whether a public URL is required or a local demonstration with video is acceptable.
3. **MCP Tool Integration:** Test tools against standard MCP inspector and document interaction traces.
4. **Dependency versions:** Freeze the versions that have passed tests in the development environment.

## Final technical recommendation

Build a **single-process Python + Streamlit application with a JSON question bank, a deterministic adaptive engine, a validated local evaluator, and a self-hosted Model Context Protocol (MCP) server for Alexa+ Agent Skills**.

This architecture gives you a working offline-capable core first, directly fulfills the "Build, Ship, Shape" Amazon Developer Hackathon primary track (Alexa+ MCP Agent Skills), and avoids adding infrastructure that does not directly improve the interview-coaching experience.
