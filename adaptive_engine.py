"""
EduAgent Interview Coach — Adaptive Question Selection & Mastery Engine
========================================================================

Implements deterministic, rule-based adaptive follow-up selection and
session concept mastery tracking matching PRD Section 10.2 and TRD Section 9.

Key design guarantees:
1. Deterministic: Given the same session state and evaluation, the same next
   question and explanation are always selected.
2. Loop-free: Questions already asked in the active session are strictly excluded.
3. Fallback-safe: If preferred follow-ups are exhausted, it gracefully falls back
   to alternative bank questions or signals interview completion.
4. Explainable: Returns user-friendly rationale explaining why each question was selected.
"""

from typing import Any, Dict, List, Optional, Set, Tuple, Union


class AdaptiveDecision:
    """
    Represents the output of the adaptive selection engine.
    """

    def __init__(
        self,
        next_question: Optional[Dict[str, Any]],
        internal_reason: str,
        student_explanation: str,
    ):
        self.next_question = next_question
        self.internal_reason = internal_reason
        self.student_explanation = student_explanation

    def to_dict(self) -> Dict[str, Any]:
        return {
            "next_question_id": self.next_question["id"] if self.next_question else None,
            "internal_reason": self.internal_reason,
            "student_explanation": self.student_explanation,
        }


class AdaptiveEngine:
    """
    Coordinates question progression and concept mastery tracking.
    """

    def __init__(self, question_bank: Optional[Union[List[Dict[str, Any]], Dict[str, Dict[str, Any]]]] = None):
        """
        Initialize the adaptive engine with an optional question bank.
        Accepts either a list of question dicts or a mapping of id -> question dict.
        """
        self._bank_map: Dict[str, Dict[str, Any]] = {}
        if question_bank is not None:
            self.set_question_bank(question_bank)

    def set_question_bank(self, question_bank: Union[List[Dict[str, Any]], Dict[str, Dict[str, Any]]]) -> None:
        """Loads or updates the active question bank."""
        if isinstance(question_bank, dict):
            self._bank_map = dict(question_bank)
        elif isinstance(question_bank, list):
            self._bank_map = {q["id"]: q for q in question_bank if isinstance(q, dict) and "id" in q}
        else:
            raise ValueError(f"Invalid question_bank type: {type(question_bank).__name__}")

    def get_question_by_id(self, question_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve question dict by ID."""
        return self._bank_map.get(question_id)

    def update_concept_tracking(
        self,
        current_question: Dict[str, Any],
        evaluation: Dict[str, Any],
        demonstrated_concepts: Set[str],
        unresolved_concepts: Set[str],
    ) -> Tuple[Set[str], Set[str]]:
        """
        Updates session-level concept mastery based on evaluation outcome.
        
        Rules:
        - Score >= 8 and no critical misconceptions:
            Concepts of current question are marked demonstrated and removed from unresolved.
        - Score < 8, or missing concepts, or misconceptions present:
            Missing concepts and misconceptions are added to unresolved concepts.
        """
        score = evaluation.get("score", 0)
        misconceptions = evaluation.get("misconceptions", [])
        missing = evaluation.get("missing_concepts", [])
        question_concepts = set(current_question.get("concepts", []))

        # Check for strong mastery
        if score >= 8 and len(misconceptions) == 0:
            demonstrated_concepts.update(question_concepts)
            # Remove any concepts now demonstrated
            unresolved_concepts.difference_update(question_concepts)
        else:
            # Add identified gaps to unresolved
            for item in missing:
                unresolved_concepts.add(item)
            for item in misconceptions:
                unresolved_concepts.add(f"Misconception: {item}")
            # If weak answer (score <= 4), track current question concepts as needing work
            if score <= 4:
                for c in question_concepts:
                    if c not in demonstrated_concepts:
                        unresolved_concepts.add(c)

        return demonstrated_concepts, unresolved_concepts

    def select_next_question(
        self,
        current_question: Dict[str, Any],
        evaluation: Dict[str, Any],
        asked_question_ids: Union[Set[str], List[str]],
        question_bank: Optional[Union[List[Dict[str, Any]], Dict[str, Dict[str, Any]]]] = None,
    ) -> AdaptiveDecision:
        """
        Selects the next interview question deterministically based on student performance.

        Parameters:
            current_question: The question just completed.
            evaluation: The validated evaluation result from evaluator.py.
            asked_question_ids: IDs already presented in the current session (to prevent repetition).
            question_bank: Optional override for the question bank.

        Returns:
            AdaptiveDecision with next_question, internal_reason, and student_explanation.
        """
        if question_bank is not None:
            self.set_question_bank(question_bank)

        if not self._bank_map:
            return AdaptiveDecision(
                next_question=None,
                internal_reason="bank_empty",
                student_explanation="Question bank is empty.",
            )

        asked_set = set(asked_question_ids)
        score = evaluation.get("score", 0)
        action = evaluation.get("recommended_action", "targeted_follow_up")
        misconceptions = evaluation.get("misconceptions", [])
        missing_concepts = evaluation.get("missing_concepts", [])

        # Priority candidates from current question metadata
        direct_follow_ups = [
            qid for qid in current_question.get("follow_up_ids", [])
            if qid in self._bank_map and qid not in asked_set
        ]
        fallback_id = current_question.get("fallback_follow_up_id")
        fallback_candidate = (
            self._bank_map[fallback_id]
            if fallback_id and fallback_id in self._bank_map and fallback_id not in asked_set
            else None
        )

        current_difficulty = current_question.get("difficulty", "medium")
        current_topic = current_question.get("topic", "Stacks")

        # -------------------------------------------------------------
        # Path A: Strong response (Score >= 8, action == "progress")
        # -------------------------------------------------------------
        if action == "progress" or (score >= 8 and not misconceptions):
            # Prefer higher difficulty or equal difficulty among direct follow-ups
            candidate = self._pick_progressive_candidate(direct_follow_ups, current_difficulty)

            if candidate:
                diff_label = candidate.get("difficulty", "next")
                return AdaptiveDecision(
                    next_question=candidate,
                    internal_reason="mastery_demonstrated",
                    student_explanation=f"Great explanation! Advancing to a {diff_label}-level question on {candidate.get('topic', current_topic)}.",
                )

            # If direct follow-ups exhausted, pick unasked question of higher difficulty or other topic
            candidate = self._find_unasked_progressive_in_bank(asked_set, current_topic)
            if candidate:
                return AdaptiveDecision(
                    next_question=candidate,
                    internal_reason="mastery_demonstrated_alternative",
                    student_explanation="Solid grasp of this concept. Moving to explore the next topic area.",
                )

        # -------------------------------------------------------------
        # Path B: Critical misconception / Foundational gap (Score <= 4, action == "scaffold_hint")
        # -------------------------------------------------------------
        elif action == "scaffold_hint" or score <= 4 or len(misconceptions) > 0:
            # 1. Prefer fallback question if it exists and hasn't been asked
            if fallback_candidate:
                misconception_note = misconceptions[0] if misconceptions else "this foundational concept"
                return AdaptiveDecision(
                    next_question=fallback_candidate,
                    internal_reason="critical_misconception" if misconceptions else "foundational_gap",
                    student_explanation=f"Selected a foundational question to help clarify: {misconception_note}.",
                )

            # 2. Prefer an easy question on the same topic
            easy_candidate = self._find_unasked_by_criteria(asked_set, topic=current_topic, difficulty="easy")
            if easy_candidate:
                return AdaptiveDecision(
                    next_question=easy_candidate,
                    internal_reason="foundational_scaffold",
                    student_explanation=f"Let's step back and reinforce the fundamentals of {current_topic}.",
                )

            # 3. Any direct follow-up
            if direct_follow_ups:
                candidate = self._bank_map[direct_follow_ups[0]]
                return AdaptiveDecision(
                    next_question=candidate,
                    internal_reason="scaffold_fallback",
                    student_explanation="Let's practice a related aspect of this data structure.",
                )

        # -------------------------------------------------------------
        # Path C: Partial understanding (Score 5-7, action == "targeted_follow_up")
        # -------------------------------------------------------------
        else:
            gap_summary = missing_concepts[0] if missing_concepts else "key operation mechanics"

            # 1. Look for direct follow-up that addresses the missing concept
            matching_direct = self._find_follow_up_matching_concepts(direct_follow_ups, missing_concepts)
            if matching_direct:
                return AdaptiveDecision(
                    next_question=matching_direct,
                    internal_reason="targeted_follow_up",
                    student_explanation=f"Follow-up selected to practice: {gap_summary}.",
                )

            # 2. Any direct follow-up
            if direct_follow_ups:
                candidate = self._bank_map[direct_follow_ups[0]]
                return AdaptiveDecision(
                    next_question=candidate,
                    internal_reason="targeted_follow_up",
                    student_explanation=f"Follow-up selected to reinforce: {gap_summary}.",
                )

            # 3. Fallback candidate
            if fallback_candidate:
                return AdaptiveDecision(
                    next_question=fallback_candidate,
                    internal_reason="targeted_fallback",
                    student_explanation=f"Practicing related principles for {current_topic}.",
                )

        # -------------------------------------------------------------
        # Exhaustion & General Bank Fallback (Loop Prevention)
        # -------------------------------------------------------------
        # If no specific follow-up matched, pick any unasked question in the bank
        general_candidate = self._find_any_unasked(asked_set, preferred_topic=current_topic)
        if general_candidate:
            return AdaptiveDecision(
                next_question=general_candidate,
                internal_reason="bank_coverage",
                student_explanation=f"Next question selected to broaden coverage of {general_candidate.get('topic', 'DSA')}.",
            )

        # All questions in bank have been asked
        return AdaptiveDecision(
            next_question=None,
            internal_reason="interview_complete",
            student_explanation="All interview questions have been completed! Generating your final report.",
        )

    # -----------------------------------------------------------------
    # Internal Helpers
    # -----------------------------------------------------------------

    def _pick_progressive_candidate(
        self, candidate_ids: List[str], current_difficulty: str
    ) -> Optional[Dict[str, Any]]:
        """Picks a follow-up prioritizing harder or equal difficulty."""
        diff_rank = {"easy": 1, "medium": 2, "hard": 3}
        current_rank = diff_rank.get(current_difficulty, 2)

        higher = []
        equal = []
        lower = []

        for qid in candidate_ids:
            q = self._bank_map[qid]
            rank = diff_rank.get(q.get("difficulty", "medium"), 2)
            if rank > current_rank:
                higher.append(q)
            elif rank == current_rank:
                equal.append(q)
            else:
                lower.append(q)

        if higher:
            return higher[0]
        if equal:
            return equal[0]
        if lower:
            return lower[0]
        return None

    def _find_follow_up_matching_concepts(
        self, candidate_ids: List[str], missing_concepts: List[str]
    ) -> Optional[Dict[str, Any]]:
        """Finds candidate whose concept tags overlap with missing concepts."""
        missing_lower = {m.lower() for m in missing_concepts}
        for qid in candidate_ids:
            q = self._bank_map[qid]
            for concept in q.get("concepts", []):
                if any(m in concept.lower() or concept.lower() in m for m in missing_lower):
                    return q
        return None

    def _find_unasked_by_criteria(
        self, asked_set: Set[str], topic: Optional[str] = None, difficulty: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Finds any unasked question matching topic and/or difficulty."""
        for q in self._bank_map.values():
            if q["id"] in asked_set:
                continue
            if topic and q.get("topic") != topic:
                continue
            if difficulty and q.get("difficulty") != difficulty:
                continue
            return q
        return None

    def _find_unasked_progressive_in_bank(
        self, asked_set: Set[str], current_topic: str
    ) -> Optional[Dict[str, Any]]:
        """Finds unasked question in bank, switching topic or increasing difficulty."""
        other_topic = "Queues" if current_topic == "Stacks" else "Stacks"
        # Try other topic first for balanced interview
        candidate = self._find_unasked_by_criteria(asked_set, topic=other_topic)
        if candidate:
            return candidate
        # Try harder on current topic
        candidate = self._find_unasked_by_criteria(asked_set, topic=current_topic, difficulty="hard")
        if candidate:
            return candidate
        # Any remaining on current topic
        return self._find_unasked_by_criteria(asked_set, topic=current_topic)

    def _find_any_unasked(
        self, asked_set: Set[str], preferred_topic: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Finds any unasked question, preferring preferred_topic if available."""
        if preferred_topic:
            for q in self._bank_map.values():
                if q["id"] not in asked_set and q.get("topic") == preferred_topic:
                    return q
        for q in self._bank_map.values():
            if q["id"] not in asked_set:
                return q
        return None
