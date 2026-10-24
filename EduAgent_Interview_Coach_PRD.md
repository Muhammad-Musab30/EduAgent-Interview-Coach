# EduAgent Interview Coach
## Product Requirements Document (PRD)

**Document version:** 1.0  
**Date:** 21 October 2026  
**Status:** Product baseline  
**Document type:** Product Requirements Document  
**Related document:** `EduAgent_Interview_Coach_TRD.md`

---

## 1. Executive Summary

EduAgent Interview Coach is an adaptive, text-based interview practice application designed to help students prepare for technical interviews and viva examinations.

The initial version focuses exclusively on Data Structures and Algorithms (DSA), specifically **Stacks and Queues**, for a Junior Software Developer interview scenario.

Unlike a static question-and-answer practice tool, EduAgent aims to identify gaps in a student's understanding, provide actionable feedback, select targeted follow-up questions, and reassess weak concepts throughout a session.

The product will prioritize educational value, predictable behavior, transparent feedback, and a complete working demonstration over unnecessary features.

The first release will be a focused prototype suitable for a hackathon demonstration. It will not attempt to replace a human interviewer, provide a complete DSA curriculum, or guarantee interview success.

## 2. Problem Statement

Students frequently prepare for technical interviews and university viva examinations by reading notes, watching tutorials, memorizing answers, or solving predetermined questions.

These approaches can help students learn concepts, but they do not always reveal whether a student can explain a concept independently, identify mistakes in their reasoning, or respond to a follow-up question.

Many basic practice tools present a fixed set of questions and answers. They may tell students whether an answer is correct without identifying the specific concepts that are missing or adapting subsequent questions to the student's demonstrated understanding.

This creates several problems:

1. **Limited personalization:** Students with different levels of understanding receive similar practice questions.
2. **Unclear weaknesses:** Students may know that an answer is incomplete without understanding which concept they missed.
3. **Insufficient follow-up practice:** A weak answer may not lead to focused practice on the underlying misconception.
4. **Passive learning:** Reading model answers does not necessarily test the student's ability to explain a concept independently.
5. **Poor progress visibility:** Students may finish a practice session without a clear summary of demonstrated knowledge and remaining gaps.
6. **Inconsistent feedback:** Students may struggle to evaluate their own answers against the important concepts expected in a technical interview.

EduAgent Interview Coach addresses these problems by creating a structured practice session in which each submitted answer influences the next learning step.

### 2.1 Product opportunity

A focused interview coach can make practice more useful by combining structured questions, consistent evaluation criteria, targeted follow-ups, and an understandable progress report.

The product's primary differentiator is not merely generating questions or assigning scores. It is the **closed-loop learning process: assess, identify a gap, practice the gap, and reassess**.

## 3. Product Vision

Help students practice explaining technical concepts, understand their mistakes, and improve their interview readiness through personalized, feedback-driven practice.

## 4. Product Goals

### 4.1 Primary goals

- Deliver a complete text-based technical interview simulation.
- Assess students' written explanations against explicit evaluation criteria.
- Identify missing concepts and potential misconceptions.
- Adapt follow-up questions to the student's demonstrated understanding.
- Help students understand why their answers received particular feedback.
- Track progress across the current interview session.
- Produce an actionable final report.
- Keep the core experience available when external AI services are unavailable.

### 4.2 Secondary goals

- Demonstrate a practical educational use case for AI-assisted evaluation.
- Show how adaptive questioning can improve upon static practice.
- Provide a clear foundation for expanding to other DSA topics in a future version.
- Demonstrate any actual cloud or agent-tool integration required by the hackathon, if implemented and verified.

## 5. Non-Goals

The first release will not attempt to:

- Cover every DSA topic.
- Support multiple job roles or academic subjects.
- Conduct voice-based or video-based interviews.
- Analyze resumes or generate personalized career plans.
- Execute arbitrary programming submissions or evaluate coding challenges in a sandbox.
- Replace teachers, mentors, professional interviewers, or formal examinations.
- Guarantee placement, employment, or examination results.
- Provide a permanent student profile, social network, or multi-user learning management system.
- Claim that a simulated tool action is an actual external tool call.
- Claim that AI-generated scores are objectively accurate or professionally validated.

These exclusions protect the project's focus and make the first release achievable.

## 6. Target Users

### 6.1 Primary user: Student preparing for technical interviews

A student who understands some programming fundamentals but needs practice explaining concepts, answering follow-up questions, and identifying knowledge gaps.

**Needs:**
- Questions appropriate to their current level.
- Clear feedback instead of a score alone.
- Practice on concepts they have not understood.
- A simple way to review progress.

### 6.2 Secondary user: Student preparing for a viva

A student who wants to practice explaining data structures and their operations before an academic viva or oral assessment.

**Needs:**
- Conceptual questions.
- Explanations of missing ideas.
- Follow-up questions that probe understanding.
- A summary of topics requiring revision.

### 6.3 Demonstration evaluator

A hackathon judge, mentor, or reviewer assessing the usefulness, reliability, and completeness of the prototype.

**Needs:**
- A working end-to-end demonstration.
- Visible evidence of adaptive behavior.
- Understandable evaluation criteria.
- Clear differentiation between implemented, simulated, and unavailable functionality.

## 7. Product Scope

### 7.1 Initial release

| Product area | Scope |
|---|---|
| Interview role | Junior Software Developer |
| Subject | Data Structures and Algorithms |
| Topics | Stacks and Queues |
| Interaction | Text-only |
| Question source | Reviewed question set |
| Evaluation | Consistent ten-point rubric |
| Adaptation | Concept-based follow-up selection |
| Feedback | Correct points, missing concepts, misconceptions, and advice |
| Progress | Current-session tracking |
| Final output | Interview performance report |
| Offline behavior | Core practice using local evaluation and Streamlit web interface |
| Hackathon track integration | Alexa+ MCP Agent Skill (Model Context Protocol server) |

### 7.2 Topic coverage

The question set should cover the following concepts as appropriate to the selected questions:

**Stacks**
- Last In, First Out (LIFO).
- Push and pop operations.
- Peek or top operation.
- Empty-stack conditions and underflow.
- Common applications of stacks.
- Basic time complexity of stack operations.

**Queues**
- First In, First Out (FIFO).
- Enqueue and dequeue operations.
- Front and rear.
- Empty-queue conditions and underflow.
- Circular queue fundamentals.
- Common applications and basic operation complexity.

The first release does not need to test every listed concept in every session. The question bank must provide sufficient coverage to demonstrate meaningful adaptation.

## 8. Core User Journey

1. The student opens the application.
2. The student sees the interview topic, role, and session instructions.
3. The student starts a practice interview.
4. The application presents a question.
5. The student types and submits an answer.
6. The application evaluates the answer and presents feedback.
7. The application identifies a suitable next question based on the evaluation.
8. The student answers a targeted follow-up or progresses to a more challenging question.
9. The process continues until the session's completion condition is reached.
10. The student receives a final report containing performance, demonstrated concepts, unresolved weaknesses, and recommendations.

The experience should feel like a guided technical interview rather than a static quiz.

## 9. Feature Requirements

Priority definitions:

- **P0 — Must have:** Essential for a valid first release.
- **P1 — Should have:** Important improvement after the core experience works.
- **P2 — Could have:** Optional enhancement that must not delay the core release.

### 9.1 Start and session management

**FR-01 — Start interview (P0)**

The application shall allow the student to start a new interview session.

**Acceptance criteria:**
- The role and topic are visible before starting.
- A new session begins with a valid question.
- The application initializes progress tracking.
- The student receives clear instructions for answering questions.

**FR-02 — Track session progress (P0)**

The application shall track attempted questions, previous evaluations, demonstrated concepts, and unresolved concepts during the active session.

**Acceptance criteria:**
- Each accepted submission is recorded once.
- Progress updates after evaluation.
- The student can see progress through the interview.
- A new session starts with a clean state.

**FR-03 — Complete an interview (P0)**

The application shall end a session when its defined stopping condition is met.

**Acceptance criteria:**
- The application does not continue indefinitely.
- The student receives a completion message.
- The final report is available after completion.

### 9.2 Question presentation and answering

**FR-04 — Present relevant questions (P0)**

The application shall present questions from the approved Stacks and Queues question set.

**Acceptance criteria:**
- Each question has a unique identity.
- Questions have defined concepts and expected answer points.
- The displayed question matches its stored content.
- Invalid or missing question data does not silently produce fabricated questions.

**FR-05 — Accept written answers (P0)**

The student shall be able to type and submit an answer.

**Acceptance criteria:**
- Empty submissions are handled clearly.
- Valid submissions are evaluated.
- Repeated clicks do not create duplicate attempts.
- The student's input is preserved appropriately during normal interface updates.

**FR-06 — Provide hints (P0)**

The student shall be able to request a hint for the current question.

**Acceptance criteria:**
- The hint relates to the current question.
- The hint helps the student reason about the concept.
- The hint does not unexpectedly change the current question.
- Hint usage can be tracked for session feedback if included in the scoring policy.

### 9.3 Answer evaluation

**FR-07 — Evaluate answers consistently (P0)**

The application shall evaluate answers using the defined ten-point rubric.

**Acceptance criteria:**
- Each completed evaluation produces a score from 0 to 10.
- Evaluation feedback uses the same rubric throughout the session.
- The result identifies relevant correct points and missing concepts.
- Evaluation output is checked for validity before being shown.
- The score is described as practice feedback rather than a guaranteed measure of interview ability.

**FR-08 — Identify missing concepts (P0)**

The application shall identify essential concepts that the student's answer does not adequately address.

**Acceptance criteria:**
- Missing concepts relate to the current question.
- Feedback is understandable to a beginner.
- The application distinguishes missing information from an explicitly incorrect claim when possible.
- The identified gap can influence the next question.

**FR-09 — Identify possible misconceptions (P0)**

The application shall identify important incorrect claims when supported by the evaluation.

**Acceptance criteria:**
- Feedback identifies the concept involved.
- The student receives a useful correction or explanation.
- Unsupported claims about the student's understanding are avoided.
- A critical misconception can trigger a simpler follow-up question.

**FR-10 — Explain feedback (P0)**

The application shall provide actionable feedback rather than a score alone.

**Acceptance criteria:**
- The feedback acknowledges important correct elements.
- It identifies the most important gap.
- It gives a concrete suggestion for improvement.
- It does not use unnecessarily harsh or discouraging language.

### 9.4 Adaptive questioning

**FR-11 — Adapt to strong answers (P0)**

The application shall progress to an appropriate next concept or more challenging question when an answer demonstrates sufficient understanding.

**Acceptance criteria:**
- The progression follows the predefined adaptation rules.
- A critical misconception prevents automatic mastery classification.
- The next question is relevant to the session.

**FR-12 — Target incomplete answers (P0)**

The application shall select a follow-up question related to a missing essential concept when an answer is incomplete.

**Acceptance criteria:**
- The follow-up targets an identified gap.
- The feedback explains why further practice is useful.
- The application avoids repeating the exact same question unnecessarily.

**FR-13 — Support weak answers (P0)**

The application shall provide a hint and a simpler follow-up when the answer shows substantial misunderstanding.

**Acceptance criteria:**
- The follow-up targets a foundational concept.
- The student receives guidance without being told that improvement is impossible.
- The session can continue safely after a weak answer.

**FR-14 — Avoid repetitive or invalid question selection (P0)**

The application shall prevent invalid question references and avoid unnecessary repetition.

**Acceptance criteria:**
- Only valid questions can be selected.
- The application handles exhausted follow-up options.
- Cyclic follow-up relationships cannot create an infinite loop.
- The interview ends or chooses a valid alternative when no suitable follow-up remains.

**FR-15 — Track concept mastery (P0)**

The application shall maintain a session-level record of concepts that appear demonstrated and concepts that still require practice.

**Acceptance criteria:**
- Mastery status is based on the defined evaluation rules.
- Missing concepts remain visible until appropriately reassessed.
- The report distinguishes demonstrated concepts from unresolved ones.
- The application does not claim mastery based on a single high score when the evaluation identifies a critical misconception.

### 9.5 Final report

**FR-16 — Generate a final report (P0)**

The application shall summarize the completed interview.

**The report must contain:**
- Overall score or clearly defined aggregate performance.
- Number of questions attempted.
- Demonstrated concepts.
- Concepts requiring further practice.
- Important misconceptions, if any.
- Actionable recommendations.
- Evaluation mode used.

**Acceptance criteria:**
- The report reflects the actual session data.
- Unassessed concepts are not falsely marked as mastered.
- Recommendations relate to observed gaps.
- Any limitations of the evaluation are communicated appropriately.

### 9.6 Evaluation service and reliability

**FR-17 — Support local evaluation (P0)**

The core interview experience shall work without an external AI service.

**Acceptance criteria:**
- A complete session can run in local mode.
- The application does not require cloud credentials to start local practice.
- Local evaluation is clearly identified.
- Known limitations of rule-based assessment are not hidden.

**FR-18 — Support Alexa+ MCP Agent Skill (P0 / Primary Hackathon Track)**

The application shall provide a self-hosted Model Context Protocol (MCP) server that exposes EduAgent Interview Coach capabilities to Alexa+ agents, supporting the "Build, Ship, Shape" Amazon Developer Hackathon (Track: Alexa+ MCP Agent Skills).

**Acceptance criteria:**
- The application exposes standardized MCP tools: `get_interview_question`, `evaluate_student_answer`, `get_session_weaknesses`, and `generate_revision_report`.
- Each tool strictly validates its input arguments against defined schemas.
- The MCP server operates reliably over stdio or SSE transport.
- The Alexa+ agent skill can conduct an interview, query candidate weak spots, and trigger revision reports.
- Offline-first operation is maintained: the core Streamlit app and local evaluator function independently of external MCP client connections.

**FR-19 — Recover from evaluation failure (P0)**

The application shall handle invalid model responses, unavailable services, and missing configuration.

**Acceptance criteria:**
- A useful error or fallback status is displayed.
- The application does not present malformed output as a valid score.
- The session remains usable when local evaluation is available.
- Retry behavior is bounded.

### 9.7 Transparency and user experience

**FR-20 — Show evaluation mode (P0)**

The application shall distinguish local evaluation from AI-assisted evaluation.

**FR-21 — Explain adaptive decisions (P0)**

The application shall provide a brief explanation of why a follow-up question was selected.

**FR-22 — Maintain a clear interface (P0)**

The application shall provide clear question, answer, feedback, progress, and completion states.

**FR-23 — Disclose external data processing (P0)**

When external evaluation or agent connections are enabled, the application shall explain that the submitted answer and necessary question context may be processed by the connected service.

### 9.8 Optional enhancements

**FR-24 — Agent activity trace (P1)**

The application may show a short activity trace, such as “Answer evaluated,” “Missing concept identified,” and “Follow-up selected.”

The trace must reflect actual application events. Simulated actions must be explicitly labelled as simulated.

**FR-25 — Multi-Modal Alexa+ Voice & Device Extension (P2, Optional)**

The application may extend the MCP server to support multi-modal or voice-driven interactions with Alexa+ devices (such as Echo Show or Fire TV multi-screen pairing).

Any implemented extension must use supported APIs, validate inputs, and report success only after a valid response is verified.

This feature must not delay the core web application or standard MCP server release.

## 10. Evaluation and Adaptation Policy

### 10.1 Scoring rubric

| Criterion | Maximum points |
|---|---:|
| Technical correctness | 4 |
| Key concepts | 3 |
| Reasoning | 2 |
| Clarity | 1 |
| **Total** | **10** |

The rubric should be applied consistently to all relevant questions. Each question should define the essential concepts needed to assess its answer.

### 10.2 Adaptation thresholds

| Result | Interpretation | Next action |
|---|---|---|
| 8–10 with no critical misconception | Strong response | Progress to a new concept or harder question |
| 5–7, or an important missing concept | Partial understanding | Ask a targeted follow-up |
| 0–4, or a critical misconception | Foundational gap | Offer a hint and a simpler follow-up |

These thresholds are initial product rules, not empirically validated cutoffs. They may be adjusted after testing, provided the behavior remains documented and consistent.

### 10.3 Fairness and limitations

- A correct explanation should receive credit even if the wording differs from the expected answer.
- A matching keyword must not automatically establish that an answer is correct.
- The application should distinguish uncertainty from a definite error.
- The application must not claim human-level evaluation accuracy without evidence.
- The same answer may receive different evaluations from different AI models; the selected provider and evaluation mode should therefore be disclosed.
- The local evaluator should favor transparent, limited claims over unsupported semantic judgments.

## 11. User Experience Requirements

### 11.1 Start screen

The start screen must show:
- Product name and purpose.
- Interview role.
- Topic coverage.
- Instructions for written answers.
- Evaluation mode.
- A clear start action.

### 11.2 Interview screen

The interview screen must show:
- Current question.
- Topic or difficulty where useful.
- Answer input.
- Submit action.
- Hint action.
- Progress indicator.

### 11.3 Feedback screen

The feedback view must show:
- Score out of ten.
- Correct points.
- Missing concepts.
- Possible misconceptions.
- Actionable feedback.
- Reason for the next question.

### 11.4 Completion screen

The completion view must show:
- Final performance summary.
- Demonstrated and unresolved concepts.
- Suggested areas for revision.
- Evaluation-mode disclosure.
- A way to begin a new session.

### 11.5 Accessibility and usability

- Use readable text and consistent labels.
- Do not rely on color alone to communicate correctness.
- Keep feedback concise and actionable.
- Avoid unnecessary steps between questions.
- Display loading, error, and completion states clearly.

## 12. Data, Privacy, and Trust Requirements

The first version is a practice prototype and does not require user accounts.

- Session information should be used to provide feedback and produce the current report.
- The product should not claim permanent storage unless that feature is implemented.
- External AI processing must be disclosed when enabled.
- Credentials and sensitive configuration must never appear in the UI or logs.
- Student answers should not be logged unnecessarily.
- The report must not imply that practice results guarantee real-world interview performance.
- Mocked outputs and simulated actions must not be presented as verified external results.

## 13. Success Metrics and Acceptance Targets

Success must be assessed through observable product behavior rather than claims about educational outcomes that have not been measured.

### 13.1 Functional success metrics

| Metric | Initial target |
|---|---|
| Complete interview flow | 100% of defined acceptance scenarios pass |
| Valid question references | 100% of selected question IDs exist in the approved question bank |
| Score validity | 100% of displayed scores are within 0–10 |
| Duplicate submissions | No duplicate attempt from a single submission action |
| Adaptive behavior | All defined adaptation test cases pass |
| Invalid AI response handling | Every tested malformed response is rejected or safely handled |
| Local-mode operation | A complete interview works without AWS credentials |
| Final report completeness | All required report fields are present |
| Question-bank validation | Invalid IDs and missing required fields are detected before use |
| Demo reproducibility | A fresh setup can follow the README and run the application |

These targets apply to tested application behavior. They do not imply that every semantic evaluation is correct.

### 13.2 Product-quality metrics

Track the following during development and demonstration:

- **Adaptive relevance:** How often a follow-up targets the gap identified in the previous evaluation.
- **Feedback usefulness:** Whether testers can identify what to improve after reading the feedback.
- **Session completion:** Whether testers can finish a session without assistance.
- **Error recovery:** Whether the application remains usable after an evaluation failure.
- **Demo reliability:** Whether the prepared demonstration works repeatedly under the documented conditions.
- **Transparency:** Whether testers can tell which evaluation mode was used and why the next question appeared.

### 13.3 Usability validation

Before submission, ask a small group of testers to complete the interview without step-by-step guidance.

Record:
- Whether they understand the purpose of the application.
- Whether they can submit answers and request hints.
- Whether the feedback is understandable.
- Whether follow-ups appear relevant.
- Whether the final report provides useful next steps.

Do not claim user satisfaction, learning improvement, or superior accuracy without actual test evidence.

## 14. Hackathon Demonstration Criteria

The demonstration should establish five things:

1. **A real problem is addressed:** Students need practice that identifies gaps, not merely displays static answers.
2. **The core experience works:** A complete interview can be started, answered, evaluated, and completed.
3. **Adaptation is visible:** A missing concept leads to a relevant follow-up, while a strong answer leads to progression.
4. **The product is trustworthy:** Feedback, scoring limitations, and evaluation mode are clear.
5. **Claims match the implementation:** Any live Alexa+ MCP feature is demonstrated through an actual successful integration; otherwise, it is labelled optional, unavailable, or simulated.

A successful demonstration should include at least one strong answer, one incomplete answer, and one weak answer or critical misconception to show the different adaptation paths.

## 15. Risks and Mitigations

| Risk | Potential impact | Mitigation |
|---|---|---|
| Inaccurate AI evaluation | Misleading student feedback | Reviewed expected points, validation, and transparent limitations |
| Weak local evaluation | Incorrect treatment of paraphrased answers | Restrict claims, test known examples, and disclose local-mode limitations |
| Irrelevant follow-up questions | Poor adaptive experience | Explicit follow-up links, concept tags, and acceptance tests |
| Repetitive questions | Frustrating sessions | Track attempted IDs and define termination rules |
| External service outage | Interrupted interview | Local fallback and clear status |
| Unavailable MCP client / environment | Missing agent integration demo | Provide self-hosted MCP server with stdio/SSE inspection and test harness |
| Excessive scope | Incomplete submission | Prioritize P0 features and defer optional enhancements |
| Misleading performance claims | Reduced trust | Use measurable acceptance criteria and report only observed results |
| Privacy concerns | Unnecessary exposure of student answers | Disclose external processing and minimize logging |
| Unverified hackathon requirements | Ineligible or incomplete submission | Check current official rules and eligibility before finalizing the submission |

## 16. Dependencies and Assumptions

### 16.1 Product dependencies

- A reviewed question set for Stacks and Queues.
- A defined evaluation rubric.
- Explicit adaptation rules.
- Acceptance tests for the major user journeys.
- Self-hosted Model Context Protocol (MCP) server for Alexa+ agent integration.

### 16.2 Assumptions requiring verification

- The hackathon permits the proposed application category.
- The selected submission track accepts the intended implementation.
- The project can be completed within the remaining development time.
- Any MCP or other integration requirement is explicitly confirmed rather than inferred.

These assumptions must not be represented as confirmed requirements until verified.

## 17. Release Plan

### Phase 1 — Core practice experience

Deliver:
- Start screen.
- Reviewed question set.
- Written answer submission.
- Local evaluation.
- Feedback.
- Deterministic adaptive follow-ups.
- Session tracking.
- Final report.

**Exit condition:** The full interview works in local mode and the core acceptance tests pass.

### Phase 2 — Reliability and usability

Deliver:
- Improved error handling.
- Question-bank validation.
- Repeated-submission protection.
- Adaptive edge-case handling.
- Clear evaluation-mode labels.
- Complete README and test evidence.

**Exit condition:** The application can reproduce the prepared demonstration reliably.

### Phase 3 — Alexa+ MCP Integration

Deliver:
- Self-hosted MCP server (`mcp_server.py`) exposing the four interview tools.
- Verification test suite for MCP tools (`get_interview_question`, `evaluate_student_answer`, `get_session_weaknesses`, `generate_revision_report`).
- Full Alexa+ agent skill documentation and inspector instructions.
- Public deployment or local tunneling if required for demonstration.

**Exit condition:** Every included MCP tool has been tested and verified over stdio/SSE protocol.

## 18. Definition of Done

The initial product release is complete when:

- [ ] A student can start a new interview.
- [ ] The interview covers the approved Stacks and Queues questions.
- [ ] A student can submit a written answer and receive feedback.
- [ ] Evaluation includes a valid score and actionable comments.
- [ ] Missing concepts and critical misconceptions affect the next step.
- [ ] Strong, partial, and weak answers follow the documented adaptation rules.
- [ ] Invalid or repeated question selection is handled safely.
- [ ] Progress is tracked during the session.
- [ ] A complete final report is produced.
- [ ] Local mode works without external AI credentials.
- [ ] Optional integrations are labelled accurately and tested if included.
- [ ] Privacy and evaluation limitations are communicated.
- [ ] The acceptance tests pass.
- [ ] The README enables another person to reproduce the demo.
- [ ] The submission describes only features that actually exist.

## 19. Future Enhancements

Potential future versions may include:

- Additional DSA topics such as linked lists, trees, graphs, and dynamic programming.
- Multiple interview roles and difficulty levels.
- Persistent progress history.
- Personalized revision plans.
- More sophisticated evaluation validation.
- A teacher or mentor dashboard.
- Voice-based interview practice.
- Coding-question evaluation in a secure execution environment.
- Additional integrations with educational tools.

These are future opportunities, not commitments for the first release.

## 20. Relationship Between PRD and TRD

This PRD defines the product's purpose, users, scope, features, expected behavior, acceptance criteria, and success measures.

The separate TRD defines how the product will be implemented, including architecture, modules, programming languages, packages, libraries, data formats, integration decisions, and technical testing arrangements.

If an implementation choice changes, update the TRD. If the intended user experience, product scope, or acceptance criteria change, review this PRD as well.

The two documents should remain consistent without duplicating each other's detailed content.

---

## Final Product Definition

EduAgent Interview Coach is a focused, text-based DSA interview practice product that uses structured evaluation and adaptive follow-up questions to help students recognize and work on gaps in their understanding.

Its first release succeeds when it reliably completes the assess–feedback–follow-up–reassess cycle, explains its decisions, produces a useful final report, and demonstrates its capabilities honestly.