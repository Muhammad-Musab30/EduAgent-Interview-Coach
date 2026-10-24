import json
import copy
from pathlib import Path
import pytest

QUESTION_BANK_PATH = Path(__file__).parent.parent / "question_bank.json"

REQUIRED_FIELDS = {
    "id": str,
    "topic": str,
    "concepts": list,
    "difficulty": str,
    "question": str,
    "expected_points": list,
    "critical_misconceptions": list,
    "hint": str,
    "follow_up_ids": list,
    "fallback_follow_up_id": str,
}

VALID_TOPICS = {"Stacks", "Queues"}
VALID_DIFFICULTIES = {"easy", "medium", "hard"}


def validate_question_bank(questions: list) -> None:
    """
    Validates question bank schema and referential integrity per TRD Section 7.4.
    Raises ValueError on validation failure.
    """
    if not isinstance(questions, list):
        raise ValueError("Question bank must be a list of question objects.")

    if len(questions) == 0:
        raise ValueError("Question bank cannot be empty.")

    seen_ids = set()
    for q in questions:
        if not isinstance(q, dict):
            raise ValueError(f"Each question must be a dictionary object, got {type(q).__name__}.")

        qid = q.get("id")
        if not qid or not isinstance(qid, str) or not qid.strip():
            raise ValueError("Every question must have a non-empty string 'id'.")

        if qid in seen_ids:
            raise ValueError(f"Duplicate question id found: '{qid}'. IDs must be unique.")
        seen_ids.add(qid)

        for field, expected_type in REQUIRED_FIELDS.items():
            if field not in q:
                raise ValueError(f"Question '{qid}' is missing required field '{field}'.")
            if not isinstance(q[field], expected_type):
                raise ValueError(
                    f"Question '{qid}' field '{field}' must be {expected_type.__name__}, got {type(q[field]).__name__}."
                )

        if q["topic"] not in VALID_TOPICS:
            raise ValueError(f"Question '{qid}' topic '{q['topic']}' is invalid. Allowed: {VALID_TOPICS}.")

        if q["difficulty"] not in VALID_DIFFICULTIES:
            raise ValueError(f"Question '{qid}' difficulty '{q['difficulty']}' is invalid. Allowed: {VALID_DIFFICULTIES}.")

        if len(q["concepts"]) == 0:
            raise ValueError(f"Question '{qid}' has an empty 'concepts' list.")
        if not all(isinstance(c, str) and c.strip() for c in q["concepts"]):
            raise ValueError(f"Question '{qid}' concepts must be non-empty strings.")

        if len(q["expected_points"]) == 0:
            raise ValueError(f"Question '{qid}' has an empty 'expected_points' list.")
        if not all(isinstance(p, str) and p.strip() for p in q["expected_points"]):
            raise ValueError(f"Question '{qid}' expected points must be non-empty strings.")

        if not isinstance(q["hint"], str) or not q["hint"].strip():
            raise ValueError(f"Question '{qid}' must have a non-empty 'hint' string.")

    # Referential integrity check
    for q in questions:
        qid = q["id"]
        for f_id in q["follow_up_ids"]:
            if f_id not in seen_ids:
                raise ValueError(f"Question '{qid}' references nonexistent follow_up_id '{f_id}'.")
            if f_id == qid:
                raise ValueError(f"Question '{qid}' references itself as a follow_up_id (infinite loop).")

        fallback_id = q["fallback_follow_up_id"]
        if fallback_id not in seen_ids:
            raise ValueError(f"Question '{qid}' references nonexistent fallback_follow_up_id '{fallback_id}'.")


@pytest.fixture(scope="module")
def questions():
    """Load question bank JSON file."""
    assert QUESTION_BANK_PATH.exists(), f"Missing question bank at {QUESTION_BANK_PATH}"
    with open(QUESTION_BANK_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def test_real_question_bank_passes_validation(questions):
    """Verify that the actual question_bank.json passes all schema and integrity checks."""
    validate_question_bank(questions)


def test_question_count(questions):
    """Verify question bank contains at least 8 and up to 12 questions as specified in TRD."""
    assert 8 <= len(questions) <= 12, f"Expected 8-12 questions, found {len(questions)}"


def test_topic_distribution(questions):
    """Verify balanced distribution between Stacks and Queues."""
    stacks = [q for q in questions if q["topic"] == "Stacks"]
    queues = [q for q in questions if q["topic"] == "Queues"]

    assert len(stacks) >= 4, f"Expected at least 4 Stacks questions, got {len(stacks)}"
    assert len(queues) >= 4, f"Expected at least 4 Queues questions, got {len(queues)}"


def test_validation_rejects_duplicate_ids(questions):
    """Verify that questions with duplicate IDs raise ValueError."""
    bad_questions = copy.deepcopy(questions)
    bad_questions[1]["id"] = bad_questions[0]["id"]
    with pytest.raises(ValueError, match="Duplicate question id"):
        validate_question_bank(bad_questions)


def test_validation_rejects_missing_field(questions):
    """Verify that questions with a missing required field raise ValueError."""
    bad_questions = copy.deepcopy(questions)
    del bad_questions[0]["expected_points"]
    with pytest.raises(ValueError, match="missing required field 'expected_points'"):
        validate_question_bank(bad_questions)


def test_validation_rejects_invalid_follow_up_id(questions):
    """Verify that questions referencing a nonexistent follow_up_id raise ValueError."""
    bad_questions = copy.deepcopy(questions)
    bad_questions[0]["follow_up_ids"].append("nonexistent_id_999")
    with pytest.raises(ValueError, match="references nonexistent follow_up_id"):
        validate_question_bank(bad_questions)


def test_validation_rejects_self_referential_loop(questions):
    """Verify that a question referencing itself as a follow-up raises ValueError."""
    bad_questions = copy.deepcopy(questions)
    bad_questions[0]["follow_up_ids"].append(bad_questions[0]["id"])
    with pytest.raises(ValueError, match="references itself as a follow_up_id"):
        validate_question_bank(bad_questions)


def test_validation_rejects_invalid_difficulty(questions):
    """Verify that an invalid difficulty label raises ValueError."""
    bad_questions = copy.deepcopy(questions)
    bad_questions[0]["difficulty"] = "insane"
    with pytest.raises(ValueError, match="difficulty 'insane' is invalid"):
        validate_question_bank(bad_questions)
