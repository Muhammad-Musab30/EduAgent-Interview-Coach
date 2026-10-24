"""
Automated Unit Tests for Adaptive Question Selection Engine (adaptive_engine.py).
Verifies deterministic follow-up selection, concept mastery tracking,
repetition prevention, and graceful termination.
"""

import json
from pathlib import Path
import pytest

from adaptive_engine import AdaptiveEngine, AdaptiveDecision


@pytest.fixture
def question_bank():
    bank_path = Path(__file__).parent.parent / "question_bank.json"
    with open(bank_path, "r", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def engine(question_bank):
    return AdaptiveEngine(question_bank)


def test_strong_answer_progresses_to_higher_or_next_question(engine, question_bank):
    """
    PRD FR-11: A strong score (>= 8, no misconceptions) progresses to
    a higher or appropriate next question with mastery_demonstrated reason.
    """
    bank_map = {q["id"]: q for q in question_bank}
    current_q = bank_map["stack_001"]  # Easy: LIFO, push, pop

    evaluation = {
        "score": 9,
        "score_breakdown": {"technical_correctness": 4, "key_concepts": 3, "reasoning": 1, "clarity": 1},
        "correct_points": ["LIFO", "push", "pop"],
        "missing_concepts": [],
        "misconceptions": [],
        "feedback": "Flawless explanation.",
        "confidence": "high",
        "recommended_action": "progress",
        "evaluation_provider": "local",
    }

    decision = engine.select_next_question(
        current_question=current_q,
        evaluation=evaluation,
        asked_question_ids=["stack_001"],
    )

    assert decision.next_question is not None
    assert decision.next_question["id"] in current_q["follow_up_ids"]
    assert decision.next_question["id"] != "stack_001"
    assert decision.internal_reason == "mastery_demonstrated"
    assert "Advancing" in decision.student_explanation or "topic" in decision.student_explanation.lower()


def test_partial_answer_selects_targeted_follow_up(engine, question_bank):
    """
    PRD FR-12: A partial answer (score 5-7, missing concepts) targets the missing concept.
    """
    bank_map = {q["id"]: q for q in question_bank}
    current_q = bank_map["stack_001"]

    evaluation = {
        "score": 6,
        "score_breakdown": {"technical_correctness": 2, "key_concepts": 2, "reasoning": 1, "clarity": 1},
        "correct_points": ["LIFO"],
        "missing_concepts": ["top element inspection", "underflow"],
        "misconceptions": [],
        "feedback": "Underflow not mentioned.",
        "confidence": "high",
        "recommended_action": "targeted_follow_up",
        "evaluation_provider": "local",
    }

    decision = engine.select_next_question(
        current_question=current_q,
        evaluation=evaluation,
        asked_question_ids=["stack_001"],
    )

    assert decision.next_question is not None
    assert decision.next_question["id"] != "stack_001"
    assert decision.internal_reason in ("targeted_follow_up", "targeted_fallback")
    assert "practice" in decision.student_explanation.lower() or "reinforce" in decision.student_explanation.lower()


def test_critical_misconception_triggers_scaffolded_fallback(engine, question_bank):
    """
    PRD FR-13: A critical misconception or low score (<= 4) selects
    the fallback question or foundational scaffolding.
    """
    bank_map = {q["id"]: q for q in question_bank}
    current_q = bank_map["stack_001"]

    evaluation = {
        "score": 3,
        "score_breakdown": {"technical_correctness": 1, "key_concepts": 1, "reasoning": 0, "clarity": 1},
        "correct_points": [],
        "missing_concepts": ["LIFO order"],
        "misconceptions": ["Claimed stacks are First In First Out (FIFO)"],
        "feedback": "Misconception detected: stacks are LIFO, not FIFO.",
        "confidence": "high",
        "recommended_action": "scaffold_hint",
        "evaluation_provider": "local",
    }

    decision = engine.select_next_question(
        current_question=current_q,
        evaluation=evaluation,
        asked_question_ids=["stack_001"],
    )

    assert decision.next_question is not None
    assert decision.next_question["id"] != "stack_001"
    # Should select fallback_follow_up_id (stack_002)
    assert decision.next_question["id"] == current_q["fallback_follow_up_id"]
    assert decision.internal_reason == "critical_misconception"
    assert "foundational" in decision.student_explanation.lower()


def test_asked_questions_are_strictly_excluded(engine, question_bank):
    """
    PRD FR-14: Questions already asked in the active session can never be selected again.
    """
    bank_map = {q["id"]: q for q in question_bank}
    current_q = bank_map["stack_001"]

    # Mark all direct follow-ups as already asked
    asked = ["stack_001", "stack_002", "stack_003"]

    evaluation = {
        "score": 9,
        "score_breakdown": {"technical_correctness": 4, "key_concepts": 3, "reasoning": 1, "clarity": 1},
        "correct_points": ["LIFO", "push", "pop"],
        "missing_concepts": [],
        "misconceptions": [],
        "feedback": "Excellent.",
        "confidence": "high",
        "recommended_action": "progress",
        "evaluation_provider": "local",
    }

    decision = engine.select_next_question(
        current_question=current_q,
        evaluation=evaluation,
        asked_question_ids=asked,
    )

    assert decision.next_question is not None
    # Must NOT be any of the asked questions
    assert decision.next_question["id"] not in asked


def test_exhausted_bank_terminates_gracefully(engine, question_bank):
    """
    PRD FR-03, FR-14: When all questions in the bank have been asked,
    the engine returns next_question=None and marks interview_complete.
    """
    bank_map = {q["id"]: q for q in question_bank}
    all_ids = list(bank_map.keys())
    current_q = bank_map[all_ids[-1]]

    evaluation = {
        "score": 8,
        "score_breakdown": {"technical_correctness": 3, "key_concepts": 3, "reasoning": 1, "clarity": 1},
        "correct_points": ["amortized analysis"],
        "missing_concepts": [],
        "misconceptions": [],
        "feedback": "Complete.",
        "confidence": "high",
        "recommended_action": "progress",
        "evaluation_provider": "local",
    }

    decision = engine.select_next_question(
        current_question=current_q,
        evaluation=evaluation,
        asked_question_ids=all_ids,
    )

    assert decision.next_question is None
    assert decision.internal_reason == "interview_complete"
    assert "completed" in decision.student_explanation.lower()


def test_cyclic_links_do_not_infinite_loop(engine, question_bank):
    """
    PRD FR-14: Cyclic follow-up references in metadata cannot cause infinite loops.
    """
    bank_map = {q["id"]: q for q in question_bank}
    current_q = bank_map["stack_001"]
    asked = set()

    for step in range(len(question_bank) + 2):
        asked.add(current_q["id"])
        eval_stub = {
            "score": 8,
            "missing_concepts": [],
            "misconceptions": [],
            "recommended_action": "progress",
        }
        decision = engine.select_next_question(current_q, eval_stub, asked)
        if decision.next_question is None:
            assert decision.internal_reason == "interview_complete"
            break
        assert decision.next_question["id"] not in asked
        current_q = decision.next_question


def test_mastery_tracking_updates_demonstrated_and_unresolved():
    """
    PRD FR-15: Verify update_concept_tracking accurately separates
    demonstrated concepts from unresolved concepts.
    """
    engine = AdaptiveEngine()

    q_stack = {
        "id": "stack_001",
        "concepts": ["LIFO", "push", "pop"],
    }

    demonstrated = set()
    unresolved = set()

    # Step 1: Weak answer with misconception
    eval_weak = {
        "score": 3,
        "missing_concepts": ["pop operation"],
        "misconceptions": ["Queue is LIFO"],
    }
    demonstrated, unresolved = engine.update_concept_tracking(
        q_stack, eval_weak, demonstrated, unresolved
    )
    assert len(demonstrated) == 0
    assert "pop operation" in unresolved
    assert "Misconception: Queue is LIFO" in unresolved

    # Step 2: Mastery demonstrated on follow-up
    eval_strong = {
        "score": 9,
        "missing_concepts": [],
        "misconceptions": [],
    }
    demonstrated, unresolved = engine.update_concept_tracking(
        q_stack, eval_strong, demonstrated, unresolved
    )
    assert "LIFO" in demonstrated
    assert "push" in demonstrated
    assert "pop" in demonstrated
    # Demonstrated concepts should be removed from unresolved
    assert "push" not in unresolved
    assert "LIFO" not in unresolved


def test_empty_bank_returns_none_safely():
    """Verify engine handles empty question bank safely."""
    empty_engine = AdaptiveEngine({})
    dummy_q = {"id": "dummy", "follow_up_ids": [], "concepts": []}
    decision = empty_engine.select_next_question(dummy_q, {"score": 5}, [])
    assert decision.next_question is None
    assert decision.internal_reason == "bank_empty"
