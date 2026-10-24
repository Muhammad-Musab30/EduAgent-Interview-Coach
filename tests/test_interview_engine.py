"""
Automated Unit Tests for Interview Session Engine (interview_engine.py).
Tests session lifecycle, submission deduplication, hint tracking,
state serialization, and completion transitions.
"""

from pathlib import Path
import pytest

from interview_engine import InterviewEngine, InterviewSession


@pytest.fixture
def engine():
    return InterviewEngine()


def test_start_session_defaults(engine):
    """
    PRD FR-01, FR-02: Starting a session defaults to 'stack_001',
    initializes clean state, and sets status to 'in_progress'.
    """
    session = engine.start_session()
    assert session.session_id.startswith("edu_")
    assert session.current_question_id == "stack_001"
    assert session.session_status == "in_progress"
    assert session.asked_question_ids == ["stack_001"]
    assert len(session.attempts) == 0
    assert len(session.demonstrated_concepts) == 0
    assert len(session.unresolved_concepts) == 0
    assert session.total_score == 0
    assert session.average_score == 0.0


def test_start_session_custom_id(engine):
    """Verify session can start with a valid custom question ID."""
    session = engine.start_session(first_question_id="queue_001")
    assert session.current_question_id == "queue_001"
    assert session.asked_question_ids == ["queue_001"]


def test_start_session_invalid_id_raises_error(engine):
    """Verify starting with non-existent question ID raises ValueError."""
    with pytest.raises(ValueError, match="not found in question bank"):
        engine.start_session(first_question_id="non_existent_999")


def test_get_current_question(engine):
    """Verify get_current_question returns matching question dict."""
    session = engine.start_session(first_question_id="stack_001")
    q = engine.get_current_question(session)
    assert q is not None
    assert q["id"] == "stack_001"
    assert q["topic"] == "Stacks"
    assert "push" in q["expected_points"] or "LIFO" in q["concepts"]


def test_request_hint(engine):
    """
    PRD FR-06: Requesting a hint retrieves the hint string,
    marks hint_requested_for_current=True, and increments hints_used_count.
    Calling hint multiple times on the same question does not double-count.
    """
    session = engine.start_session(first_question_id="stack_001")
    assert not session.hint_requested_for_current
    assert session.hints_used_count == 0

    hint1 = engine.request_hint(session)
    assert len(hint1) > 0
    assert session.hint_requested_for_current
    assert session.hints_used_count == 1

    # Calling again on same question should not increment count
    hint2 = engine.request_hint(session)
    assert hint2 == hint1
    assert session.hints_used_count == 1


def test_empty_answer_submission(engine):
    """
    PRD FR-05: Submitting empty or whitespace answer returns score 0,
    does not advance question, and does not record a completed attempt.
    """
    session = engine.start_session(first_question_id="stack_001")
    eval_res, decision, is_done = engine.submit_answer(session, "   ")

    assert eval_res["score"] == 0
    assert not is_done
    assert session.current_question_id == "stack_001"
    assert len(session.attempts) == 0
    assert "Write an answer" in eval_res["feedback"]


def test_duplicate_submission_protection(engine):
    """
    PRD FR-05, TRD Section 15: Rapid duplicate clicks with the same answer
    do not register multiple attempts.
    """
    session = engine.start_session(first_question_id="stack_001")
    answer = "A stack is Last In First Out (LIFO). Push adds to the top and pop removes from the top."

    # First submission
    eval1, dec1, done1 = engine.submit_answer(session, answer)
    initial_attempts = len(session.attempts)
    assert initial_attempts == 1

    # Second submission with exact same text immediately after
    eval2, dec2, done2 = engine.submit_answer(session, answer)
    assert len(session.attempts) == 1  # Deduplicated!
    assert eval2["score"] == eval1["score"]


def test_valid_submission_progression_and_mastery(engine):
    """
    PRD FR-02, FR-11, FR-15: A strong answer advances to the next question,
    records the attempt, updates demonstrated concepts, and resets hint flag.
    """
    session = engine.start_session(first_question_id="stack_001")
    engine.request_hint(session)
    assert session.hint_requested_for_current

    answer = (
        "A stack is a linear data structure following Last In First Out (LIFO). "
        "The push operation inserts an element onto the top of the stack, "
        "and pop removes the most recently added element from the top."
    )

    eval_res, decision, is_done = engine.submit_answer(session, answer)

    assert eval_res["score"] >= 8
    assert len(session.attempts) == 1
    assert session.attempts[0]["hint_used"] is True
    assert session.attempts[0]["question_id"] == "stack_001"

    # Must have advanced to a new question
    assert session.current_question_id != "stack_001"
    assert session.current_question_id in session.asked_question_ids
    # Hint flag reset for the new question
    assert not session.hint_requested_for_current

    # Demonstrated concepts must be populated
    assert "LIFO" in session.demonstrated_concepts or "push" in session.demonstrated_concepts


def test_score_aggregates(engine):
    """Verify total_score and average_score calculations."""
    session = engine.start_session(first_question_id="stack_001")

    # Attempt 1: score 10
    ans1 = "A stack is Last In First Out (LIFO). Push adds to the top and pop removes from the top."
    engine.submit_answer(session, ans1)

    # Attempt 2: partial answer
    ans2 = "It is an operation."
    engine.submit_answer(session, ans2)

    assert session.total_score > 0
    assert session.average_score > 0.0
    assert session.average_score == round(session.total_score / 2, 1)


def test_explicit_end_session(engine):
    """PRD FR-03: Ending a session updates session_status to completed."""
    session = engine.start_session()
    assert session.session_status == "in_progress"

    engine.end_session(session)
    assert session.session_status == "completed"

    with pytest.raises(ValueError, match="already completed"):
        engine.submit_answer(session, "Late answer")


def test_session_serialization_round_trip(engine):
    """
    TRD Section 10: Verify InterviewSession.to_dict() and from_dict()
    perform a flawless round-trip conversion for Streamlit session state.
    """
    session = engine.start_session(first_question_id="stack_001")
    engine.request_hint(session)
    answer = "A stack is LIFO. Push puts on top and pop takes off top."
    engine.submit_answer(session, answer)

    data = session.to_dict()
    assert isinstance(data, dict)
    assert isinstance(data["demonstrated_concepts"], list)
    assert isinstance(data["unresolved_concepts"], list)

    restored = InterviewSession.from_dict(data)
    assert restored.session_id == session.session_id
    assert restored.current_question_id == session.current_question_id
    assert restored.session_status == session.session_status
    assert restored.hints_used_count == session.hints_used_count
    assert len(restored.attempts) == len(session.attempts)
    assert restored.demonstrated_concepts == session.demonstrated_concepts
    assert restored.unresolved_concepts == session.unresolved_concepts
    assert restored.total_score == session.total_score
