"""
Automated Unit Tests for Final Report Generator (report_generator.py).
Verifies report schema completeness, tier calculations, recommendation logic,
and markdown rendering per PRD FR-16 and TRD Section 13.1.
"""

import pytest

from interview_engine import InterviewEngine, InterviewSession
from report_generator import ReportGenerator


@pytest.fixture
def engine():
    return InterviewEngine()


def test_report_schema_completeness(engine):
    """
    PRD FR-16: Verify that all required fields are present in the generated report.
    """
    session = engine.start_session()
    ans = "A stack is a Last In First Out (LIFO) structure. Push adds to top and pop removes from top."
    engine.submit_answer(session, ans)

    report = ReportGenerator.generate_report(session)

    required_fields = [
        "session_id",
        "created_at",
        "evaluation_mode",
        "attempts_count",
        "total_score",
        "max_possible_score",
        "average_score",
        "percentage",
        "performance_tier",
        "tier_summary",
        "hints_used",
        "demonstrated_concepts",
        "unresolved_concepts",
        "misconceptions_detected",
        "recommendations",
        "question_summaries",
        "disclaimer",
    ]

    for field in required_fields:
        assert field in report, f"Missing required report field: '{field}'"

    assert report["attempts_count"] == 1
    assert report["max_possible_score"] == 10
    assert 0 <= report["percentage"] <= 100.0


def test_proficient_tier_report(engine):
    """Verify strong performance produces 'Proficient' tier."""
    session = engine.start_session(first_question_id="stack_001")
    ans = "A stack is a Last In First Out (LIFO) structure. Push adds to top and pop removes from top."
    eval_res, _, _ = engine.submit_answer(session, ans)
    assert eval_res["score"] >= 8

    report = ReportGenerator.generate_report(session)
    assert report["performance_tier"] == "Proficient"
    assert report["percentage"] >= 80.0
    assert len(report["demonstrated_concepts"]) > 0
    assert len(report["recommendations"]) > 0


def test_developing_tier_report(engine):
    """Verify partial performance produces 'Developing' tier."""
    session = engine.start_session(first_question_id="stack_001")
    ans = "A stack is LIFO."  # Partial answer
    engine.submit_answer(session, ans)

    report = ReportGenerator.generate_report(session)
    # Score should be partial (around 5-7), meaning Developing tier
    assert report["performance_tier"] in ("Developing", "Foundational")
    assert report["percentage"] < 80.0


def test_foundational_tier_with_misconception(engine):
    """
    Verify answer with critical misconception produces 'Foundational' tier
    and extracts the misconception into misconceptions_detected.
    """
    session = engine.start_session(first_question_id="stack_001")
    ans = "A stack is a collection where pop removes the oldest or bottom element from the stack."
    engine.submit_answer(session, ans)

    report = ReportGenerator.generate_report(session)
    assert report["performance_tier"] == "Foundational"
    assert len(report["misconceptions_detected"]) > 0
    assert any("bottom" in m.lower() or "oldest" in m.lower() for m in report["misconceptions_detected"])


def test_empty_session_report(engine):
    """Verify empty session with 0 attempts is handled gracefully without division by zero."""
    session = engine.start_session()
    report = ReportGenerator.generate_report(session)

    assert report["attempts_count"] == 0
    assert report["total_score"] == 0
    assert report["max_possible_score"] == 0
    assert report["percentage"] == 0.0
    assert report["performance_tier"] == "Incomplete"
    assert len(report["question_summaries"]) == 0


def test_markdown_report_formatting(engine):
    """Verify markdown generator produces structured text with expected sections."""
    session = engine.start_session()
    ans = "A stack is LIFO. Push puts an item on top and pop takes it off."
    engine.submit_answer(session, ans)

    report = ReportGenerator.generate_report(session)
    md = ReportGenerator.generate_markdown_report(report)

    assert "# EduAgent Interview Performance Report" in md
    assert "Overall Performance" in md
    assert "Demonstrated Strengths" in md
    assert "Priority Revision Recommendations" in md
    assert report["disclaimer"] in md
    assert report["session_id"] in md


def test_tailored_recommendations_for_unresolved_underflow():
    """Verify specific unresolved gaps trigger tailored advice from the catalog."""
    session_data = {
        "session_id": "test_session",
        "attempts": [
            {
                "question_id": "stack_002",
                "question_text": "Explain peek and underflow",
                "evaluation": {"score": 5, "misconceptions": []},
            }
        ],
        "demonstrated_concepts": ["top element"],
        "unresolved_concepts": ["underflow handling", "empty stack check"],
        "hints_used_count": 0,
        "evaluation_provider": "local",
    }

    report = ReportGenerator.generate_report(session_data)
    recs = " ".join(report["recommendations"]).lower()
    assert "underflow" in recs or "empty" in recs
