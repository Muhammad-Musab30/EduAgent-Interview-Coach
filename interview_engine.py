"""
EduAgent Interview Coach — Interview Session Engine & Lifecycle Coordinator
============================================================================

Coordinates session initialization, submission deduplication, hint retrieval,
answer evaluation, and adaptive progression matching TRD Section 10 and PRD Section 9.1-9.2.

Key guarantees:
1. Framework-agnostic: Pure Python without Streamlit dependencies for clean unit testing.
2. State serializable: InterviewSession can be exported to and imported from standard dictionaries.
3. Deduplication: Prevents double-submission from registering duplicate attempts.
4. Safe lifecycle: Clear transitions from "in_progress" to "completed".
"""

import datetime
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union
import uuid

from adaptive_engine import AdaptiveDecision, AdaptiveEngine
from evaluator import evaluate_answer


class InterviewSession:
    """
    Encapsulates all mutable state for an active technical interview session.
    Matches TRD Section 10.2 schema.
    """

    def __init__(
        self,
        session_id: Optional[str] = None,
        current_question_id: str = "stack_001",
        attempts: Optional[List[Dict[str, Any]]] = None,
        demonstrated_concepts: Optional[Set[str]] = None,
        unresolved_concepts: Optional[Set[str]] = None,
        asked_question_ids: Optional[List[str]] = None,
        evaluation_provider: str = "local",
        session_status: str = "in_progress",
        hint_requested_for_current: bool = False,
        hints_used_count: int = 0,
        last_submission_hash: Optional[str] = None,
        created_at: Optional[str] = None,
    ):
        self.session_id = session_id or f"edu_{uuid.uuid4().hex[:8]}"
        self.current_question_id = current_question_id
        self.attempts: List[Dict[str, Any]] = attempts if attempts is not None else []
        self.demonstrated_concepts: Set[str] = (
            set(demonstrated_concepts) if demonstrated_concepts is not None else set()
        )
        self.unresolved_concepts: Set[str] = (
            set(unresolved_concepts) if unresolved_concepts is not None else set()
        )
        self.asked_question_ids: List[str] = (
            list(asked_question_ids) if asked_question_ids is not None else [current_question_id]
        )
        self.evaluation_provider = evaluation_provider
        self.session_status = session_status  # "in_progress" or "completed"
        self.hint_requested_for_current = hint_requested_for_current
        self.hints_used_count = hints_used_count
        self.last_submission_hash = last_submission_hash
        self.created_at = created_at or datetime.datetime.now().isoformat()

    @property
    def total_score(self) -> int:
        """Returns the sum of all scores received across valid attempts."""
        return sum(
            att.get("evaluation", {}).get("score", 0)
            for att in self.attempts
            if isinstance(att.get("evaluation"), dict)
        )

    @property
    def average_score(self) -> float:
        """Returns the mean score per completed attempt (0.0 if no attempts)."""
        valid_attempts = [
            att for att in self.attempts
            if isinstance(att.get("evaluation"), dict) and "score" in att["evaluation"]
        ]
        if not valid_attempts:
            return 0.0
        return round(self.total_score / len(valid_attempts), 1)

    def to_dict(self) -> Dict[str, Any]:
        """Serializes session state to a standard dict suitable for st.session_state or JSON."""
        return {
            "session_id": self.session_id,
            "current_question_id": self.current_question_id,
            "attempts": self.attempts,
            "demonstrated_concepts": sorted(list(self.demonstrated_concepts)),
            "unresolved_concepts": sorted(list(self.unresolved_concepts)),
            "asked_question_ids": list(self.asked_question_ids),
            "evaluation_provider": self.evaluation_provider,
            "session_status": self.session_status,
            "hint_requested_for_current": self.hint_requested_for_current,
            "hints_used_count": self.hints_used_count,
            "last_submission_hash": self.last_submission_hash,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "InterviewSession":
        """Reconstructs an InterviewSession instance from a serialized dict."""
        return cls(
            session_id=data.get("session_id"),
            current_question_id=data.get("current_question_id", "stack_001"),
            attempts=data.get("attempts", []),
            demonstrated_concepts=set(data.get("demonstrated_concepts", [])),
            unresolved_concepts=set(data.get("unresolved_concepts", [])),
            asked_question_ids=data.get("asked_question_ids", []),
            evaluation_provider=data.get("evaluation_provider", "local"),
            session_status=data.get("session_status", "in_progress"),
            hint_requested_for_current=data.get("hint_requested_for_current", False),
            hints_used_count=data.get("hints_used_count", 0),
            last_submission_hash=data.get("last_submission_hash"),
            created_at=data.get("created_at"),
        )


class InterviewEngine:
    """
    Coordinates session creation, answer evaluation, question progression,
    and completion detection.
    """

    def __init__(
        self,
        question_bank_path: Optional[Union[str, Path]] = None,
        question_bank: Optional[Union[List[Dict[str, Any]], Dict[str, Dict[str, Any]]]] = None,
    ):
        """
        Initializes the interview engine. Loads the question bank from disk if not provided.
        """
        if question_bank is not None:
            if isinstance(question_bank, list):
                self._bank = {q["id"]: q for q in question_bank if "id" in q}
            elif isinstance(question_bank, dict):
                self._bank = dict(question_bank)
            else:
                raise ValueError("question_bank must be a list or dict.")
        else:
            if question_bank_path is None:
                question_bank_path = Path(__file__).parent / "question_bank.json"
            else:
                question_bank_path = Path(question_bank_path)

            if not question_bank_path.exists():
                raise FileNotFoundError(f"Question bank file not found: {question_bank_path}")

            with open(question_bank_path, "r", encoding="utf-8") as f:
                questions_data = json.load(f)
                self._bank = {q["id"]: q for q in questions_data if "id" in q}

        if not self._bank:
            raise ValueError("Question bank is empty. At least one question required.")

        self.adaptive_engine = AdaptiveEngine(self._bank)

    @property
    def question_count(self) -> int:
        return len(self._bank)

    def get_question(self, question_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve question data by ID."""
        return self._bank.get(question_id)

    def start_session(
        self,
        first_question_id: Optional[str] = None,
        provider: str = "local",
    ) -> InterviewSession:
        """
        Starts a new interview session.
        If first_question_id is not specified, uses 'stack_001' or the first available question.
        """
        if first_question_id is None:
            first_question_id = "stack_001" if "stack_001" in self._bank else next(iter(self._bank.keys()))
        elif first_question_id not in self._bank:
            raise ValueError(f"Initial question ID '{first_question_id}' not found in question bank.")

        return InterviewSession(
            current_question_id=first_question_id,
            evaluation_provider=provider,
            session_status="in_progress",
        )

    def get_current_question(self, session: InterviewSession) -> Optional[Dict[str, Any]]:
        """Returns the question dict for the active question in the session."""
        return self._bank.get(session.current_question_id)

    def request_hint(self, session: InterviewSession) -> str:
        """
        Records hint request for the current question and returns the hint text.
        """
        q = self.get_current_question(session)
        if not q:
            return "No hint available."

        if not session.hint_requested_for_current:
            session.hint_requested_for_current = True
            session.hints_used_count += 1

        return q.get("hint", "Explain the core mechanics and definition of this concept.")

    def submit_answer(
        self,
        session: InterviewSession,
        answer_text: str,
        question_id: Optional[str] = None,
    ) -> Tuple[Dict[str, Any], AdaptiveDecision, bool]:
        """
        Processes a student's answer submission.

        Parameters:
            session: The active InterviewSession.
            answer_text: The student's written response.
            question_id: Optional ID of the question the student intended to answer.

        Returns:
            (evaluation_result, adaptive_decision, session_completed)
        """
        if session.session_status == "completed":
            raise ValueError("Cannot submit an answer to an already completed session.")

        current_q = self.get_current_question(session)
        if not current_q:
            raise ValueError(f"Current question '{session.current_question_id}' not found in bank.")

        clean_answer = answer_text.strip() if answer_text else ""

        # 1. Handle empty submission safely (PRD FR-05)
        if not clean_answer:
            eval_result = evaluate_answer(current_q, "", provider=session.evaluation_provider)
            decision = AdaptiveDecision(
                next_question=current_q,
                internal_reason="empty_submission",
                student_explanation="Write an answer before submitting.",
            )
            return eval_result, decision, False

        # 2. Prevent duplicate submission from rapid button clicks (PRD FR-05, TRD Section 15)
        submission_hash = hashlib.sha256(clean_answer.encode("utf-8")).hexdigest()

        # Check if identical response was submitted consecutively or for an already completed question
        is_duplicate = False
        if session.attempts and session.last_submission_hash == submission_hash:
            is_duplicate = True
        elif question_id and session.attempts and session.attempts[-1]["question_id"] == question_id:
            is_duplicate = True

        if is_duplicate and session.attempts:
            last_attempt = session.attempts[-1]
            last_eval = last_attempt["evaluation"]
            last_decision_dict = last_attempt["adaptive_decision"]
            next_q = (
                self.get_question(last_decision_dict.get("next_question_id"))
                if last_decision_dict.get("next_question_id")
                else None
            )
            restored_decision = AdaptiveDecision(
                next_question=next_q,
                internal_reason="duplicate_submission",
                student_explanation=last_decision_dict.get("student_explanation", ""),
            )
            return last_eval, restored_decision, (session.session_status == "completed")

        # 3. Evaluate the answer using rubric and local evaluator
        evaluation = evaluate_answer(
            current_q,
            clean_answer,
            provider=session.evaluation_provider,
        )

        # 4. Update session-level concept tracking
        self.adaptive_engine.update_concept_tracking(
            current_q,
            evaluation,
            session.demonstrated_concepts,
            session.unresolved_concepts,
        )

        # 5. Adaptively select the next question
        decision = self.adaptive_engine.select_next_question(
            current_question=current_q,
            evaluation=evaluation,
            asked_question_ids=session.asked_question_ids,
        )

        # 6. Record attempt history
        attempt_record: Dict[str, Any] = {
            "question_id": current_q["id"],
            "question_text": current_q.get("question", ""),
            "topic": current_q.get("topic", "DSA"),
            "difficulty": current_q.get("difficulty", "medium"),
            "student_answer": clean_answer,
            "hint_used": session.hint_requested_for_current,
            "evaluation": evaluation,
            "adaptive_decision": decision.to_dict(),
            "timestamp": datetime.datetime.now().isoformat(),
        }
        session.attempts.append(attempt_record)
        session.last_submission_hash = submission_hash

        # 7. Update session lifecycle
        if decision.next_question is None:
            session.session_status = "completed"
            is_completed = True
        else:
            session.current_question_id = decision.next_question["id"]
            if decision.next_question["id"] not in session.asked_question_ids:
                session.asked_question_ids.append(decision.next_question["id"])
            session.hint_requested_for_current = False
            is_completed = False

        return evaluation, decision, is_completed

    def end_session(self, session: InterviewSession) -> None:
        """Explicitly ends the interview session."""
        session.session_status = "completed"
