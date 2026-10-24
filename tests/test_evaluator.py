"""
test_evaluator.py — Automated Unit Tests for Answer Evaluation Engine

Tests the 10-point scoring rubric, misconception detection, empty answer handling,
bounds checking, and schema validation.
"""

import json
from pathlib import Path
import pytest
from evaluator import (
    evaluate_answer,
    validate_evaluation_result,
    LocalEvaluator,
    EvaluationResult
)

QUESTION_BANK_PATH = Path(__file__).parent.parent / "question_bank.json"


@pytest.fixture(scope="module")
def questions():
    with open(QUESTION_BANK_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {q["id"]: q for q in data}


def test_strong_stack_answer(questions):
    """Verify strong response scores 8-10, recommends progress, and has no misconceptions."""
    q = questions["stack_001"]
    answer = (
        "LIFO stands for Last In First Out, meaning the last element added is the first one removed. "
        "The push operation adds a new item onto the top of the stack. "
        "The pop operation removes and returns the top element from the stack. "
        "This is because access is strictly restricted to the top end."
    )
    result = evaluate_answer(q, answer)

    assert 8 <= result["score"] <= 10, f"Expected 8-10 for strong answer, got {result['score']}"
    assert result["recommended_action"] == "progress"
    assert len(result["misconceptions"]) == 0
    assert len(result["correct_points"]) >= 2
    assert result["score"] == sum(result["score_breakdown"].values())


def test_partial_stack_answer(questions):
    """Verify partial answer scores 5-7, identifies missing concepts, and recommends targeted follow-up."""
    q = questions["stack_001"]
    # Answer only explains push, missing pop and formal LIFO definition
    answer = "Push adds a new element onto the top of the stack."
    result = evaluate_answer(q, answer)

    assert 3 <= result["score"] <= 7, f"Expected 3-7 for partial answer, got {result['score']}"
    assert len(result["missing_concepts"]) > 0, "Missing concepts must be identified"
    assert result["recommended_action"] in {"targeted_follow_up", "scaffold_hint"}
    assert result["score"] == sum(result["score_breakdown"].values())


def test_critical_misconception_detection(questions):
    """Verify that a critical misconception is caught, penalized, and triggers scaffold hint."""
    q = questions["stack_001"]
    # Answer contains the critical misconception: pop removes the oldest element
    answer = (
        "In a stack, push adds an item to the top, but the pop operation removes the oldest or bottom element."
    )
    result = evaluate_answer(q, answer)

    assert len(result["misconceptions"]) > 0, "Expected misconception to be detected"
    assert any("oldest or bottom" in m for m in result["misconceptions"])
    assert result["score"] <= 5, f"Score with critical misconception should be penalized, got {result['score']}"
    assert result["recommended_action"] == "scaffold_hint"
    assert result["score"] == sum(result["score_breakdown"].values())


def test_empty_and_whitespace_answer(questions):
    """Verify empty or whitespace answers score 0 and provide clear feedback."""
    q = questions["stack_001"]

    for empty_input in ["", "   ", "\n\t"]:
        result = evaluate_answer(q, empty_input)
        assert result["score"] == 0
        assert result["score_breakdown"]["technical_correctness"] == 0
        assert result["score_breakdown"]["key_concepts"] == 0
        assert result["score_breakdown"]["reasoning"] == 0
        assert result["score_breakdown"]["clarity"] == 0
        assert result["recommended_action"] == "scaffold_hint"
        assert "Write an answer before submitting" in result["feedback"]
        assert len(result["missing_concepts"]) == len(q["expected_points"])


def test_strong_queue_answer(questions):
    """Verify strong Queue answer scores 8-10 with progress action."""
    q = questions["queue_001"]
    answer = (
        "FIFO means First In, First Out: the first element inserted is the first one removed. "
        "Enqueue inserts an element at the rear of the queue, while dequeue removes and returns "
        "the element at the front of the queue, preserving arrival order."
    )
    result = evaluate_answer(q, answer)

    assert 8 <= result["score"] <= 10
    assert result["recommended_action"] == "progress"
    assert len(result["misconceptions"]) == 0
    assert result["score"] == sum(result["score_breakdown"].values())


def test_queue_misconception_detection(questions):
    """Verify queue misconception (claiming queue is LIFO) is caught."""
    q = questions["queue_001"]
    answer = "A queue operates on Last In, First Out (LIFO). You enqueue at the front and dequeue at the same end."
    result = evaluate_answer(q, answer)

    assert len(result["misconceptions"]) > 0
    assert result["score"] <= 4
    assert result["recommended_action"] == "scaffold_hint"


def test_score_breakdown_bounds(questions):
    """Verify all rubric components strictly obey maximum allowed points."""
    q = questions["stack_002"]
    answers = [
        "Peek examines the top without removing it. Popping empty stack causes underflow. Overflow occurs when full.",
        "Just peek.",
        "Nothing happens",
    ]
    for ans in answers:
        result = evaluate_answer(q, ans)
        b = result["score_breakdown"]
        assert 0 <= b["technical_correctness"] <= 4
        assert 0 <= b["key_concepts"] <= 3
        assert 0 <= b["reasoning"] <= 2
        assert 0 <= b["clarity"] <= 1
        assert result["score"] == (
            b["technical_correctness"] + b["key_concepts"] + b["reasoning"] + b["clarity"]
        )


def test_schema_validator_rejects_malformed_results():
    """Verify validate_evaluation_result rejects non-compliant structures."""
    valid_sample: EvaluationResult = {
        "score": 8,
        "score_breakdown": {
            "technical_correctness": 3,
            "key_concepts": 3,
            "reasoning": 1,
            "clarity": 1,
        },
        "correct_points": ["Point A"],
        "missing_concepts": [],
        "misconceptions": [],
        "feedback": "Great job.",
        "confidence": "high",
        "recommended_action": "progress",
        "evaluation_provider": "local",
    }
    # Valid sample passes
    validate_evaluation_result(valid_sample)

    # Rejects out-of-bounds score
    bad_score = dict(valid_sample)
    bad_score["score"] = 11
    with pytest.raises(ValueError, match="Score must be between 0 and 10"):
        validate_evaluation_result(bad_score)

    # Rejects breakdown mismatch
    bad_sum = dict(valid_sample)
    bad_sum["score"] = 5
    with pytest.raises(ValueError, match="does not match sum"):
        validate_evaluation_result(bad_sum)

    # Rejects invalid action
    bad_action = dict(valid_sample)
    bad_action["recommended_action"] = "fly_to_moon"
    with pytest.raises(ValueError, match="Invalid recommended_action"):
        validate_evaluation_result(bad_action)

    # Rejects missing key
    missing_key = dict(valid_sample)
    del missing_key["feedback"]
    with pytest.raises(ValueError, match="missing required keys"):
        validate_evaluation_result(missing_key)


def test_bedrock_fallback_safely_evaluates(questions):
    """Verify that requesting bedrock provider falls back safely without credentials."""
    q = questions["stack_001"]
    ans = "Push puts an item on top of the stack and pop takes it off."
    result = evaluate_answer(q, ans, provider="bedrock")
    assert result["evaluation_provider"] == "local"
    assert 0 <= result["score"] <= 10


def test_unknown_provider_raises_error(questions):
    """Verify unknown provider raises ValueError."""
    q = questions["stack_001"]
    with pytest.raises(ValueError, match="Unknown evaluation provider"):
        evaluate_answer(q, "answer", provider="quantum_ai")
