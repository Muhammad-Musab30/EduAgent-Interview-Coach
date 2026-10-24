"""
evaluator.py — Answer Evaluation Engine

Provides the 10-point scoring rubric implementation, local rule-based evaluation,
critical misconception detection, and structured output schema validation.

PRD References: Section 9.3 (Answer evaluation), Section 10.1 (Scoring rubric), Section 10.2 (Thresholds)
TRD References: Section 8 (Evaluation Architecture)
"""

from typing import Any, Dict, List, TypedDict
import re


class ScoreBreakdown(TypedDict):
    technical_correctness: int  # 0 to 4
    key_concepts: int           # 0 to 3
    reasoning: int              # 0 to 2
    clarity: int                # 0 to 1


class EvaluationResult(TypedDict):
    score: int
    score_breakdown: ScoreBreakdown
    correct_points: List[str]
    missing_concepts: List[str]
    misconceptions: List[str]
    feedback: str
    confidence: str
    recommended_action: str
    evaluation_provider: str


ALLOWED_CONFIDENCE = {"high", "medium", "low"}
ALLOWED_ACTIONS = {"progress", "targeted_follow_up", "scaffold_hint"}
ALLOWED_PROVIDERS = {"local", "bedrock"}


def validate_evaluation_result(result: Dict[str, Any]) -> None:
    """
    Validates that an evaluation result adheres strictly to the TRD schema and rubric bounds.
    Raises ValueError if validation fails.
    """
    if not isinstance(result, dict):
        raise ValueError(f"Evaluation result must be a dictionary, got {type(result).__name__}.")

    required_keys = {
        "score", "score_breakdown", "correct_points", "missing_concepts",
        "misconceptions", "feedback", "confidence", "recommended_action",
        "evaluation_provider"
    }
    missing = required_keys - set(result.keys())
    if missing:
        raise ValueError(f"Evaluation result missing required keys: {sorted(list(missing))}")

    score = result["score"]
    if not isinstance(score, int) or isinstance(score, bool):
        raise ValueError(f"Score must be an integer, got {type(score).__name__}.")
    if not (0 <= score <= 10):
        raise ValueError(f"Score must be between 0 and 10, got {score}.")

    breakdown = result["score_breakdown"]
    if not isinstance(breakdown, dict):
        raise ValueError("score_breakdown must be a dictionary.")

    breakdown_keys = {"technical_correctness", "key_concepts", "reasoning", "clarity"}
    missing_b = breakdown_keys - set(breakdown.keys())
    if missing_b:
        raise ValueError(f"score_breakdown missing required keys: {sorted(list(missing_b))}")

    tc = breakdown["technical_correctness"]
    kc = breakdown["key_concepts"]
    re_pt = breakdown["reasoning"]
    cl = breakdown["clarity"]

    if not (isinstance(tc, int) and 0 <= tc <= 4):
        raise ValueError(f"technical_correctness must be an int between 0 and 4, got {tc}.")
    if not (isinstance(kc, int) and 0 <= kc <= 3):
        raise ValueError(f"key_concepts must be an int between 0 and 3, got {kc}.")
    if not (isinstance(re_pt, int) and 0 <= re_pt <= 2):
        raise ValueError(f"reasoning must be an int between 0 and 2, got {re_pt}.")
    if not (isinstance(cl, int) and 0 <= cl <= 1):
        raise ValueError(f"clarity must be an int between 0 and 1, got {cl}.")

    if score != (tc + kc + re_pt + cl):
        raise ValueError(
            f"Overall score ({score}) does not match sum of breakdown points ({tc + kc + re_pt + cl})."
        )

    for list_field in ["correct_points", "missing_concepts", "misconceptions"]:
        if not isinstance(result[list_field], list):
            raise ValueError(f"Field '{list_field}' must be a list.")
        if not all(isinstance(item, str) for item in result[list_field]):
            raise ValueError(f"All elements in '{list_field}' must be strings.")

    if not isinstance(result["feedback"], str) or not result["feedback"].strip():
        raise ValueError("Feedback must be a non-empty string.")

    if result["confidence"] not in ALLOWED_CONFIDENCE:
        raise ValueError(f"Invalid confidence '{result['confidence']}'. Allowed: {ALLOWED_CONFIDENCE}")

    if result["recommended_action"] not in ALLOWED_ACTIONS:
        raise ValueError(f"Invalid recommended_action '{result['recommended_action']}'. Allowed: {ALLOWED_ACTIONS}")

    if result["evaluation_provider"] not in ALLOWED_PROVIDERS:
        raise ValueError(f"Invalid evaluation_provider '{result['evaluation_provider']}'. Allowed: {ALLOWED_PROVIDERS}")


class LocalEvaluator:
    """
    Deterministic offline evaluator implementing the 10-point scoring rubric.
    Evaluates student answers against expected points and detects critical misconceptions.
    """

    # Conceptual keyword / phrase clusters for robust matching without external LLM
    CONCEPT_SYNONYMS = {
        "lifo": [r"\blifo\b", r"last[\s-]in[\s,]+first[\s-]out", r"last added.*first removed"],
        "push": [r"\bpush\b", r"add.*top", r"insert.*top", r"place.*top"],
        "pop": [r"\bpop\b", r"remove.*top", r"delete.*top", r"take.*top"],
        "peek": [r"\bpeek\b", r"\btop\b", r"without removing", r"examine.*top", r"look at.*top"],
        "underflow": [r"\bunderflow\b", r"empty (stack|queue)", r"no elements? to (pop|remove|dequeue)"],
        "overflow": [r"\boverflow\b", r"full (stack|queue)", r"exceed.*capacity"],
        "applications": [r"call stack", r"recursion", r"parenthes", r"undo", r"redo", r"scheduling", r"buffer", r"bfs", r"breadth-first"],
        "time_complexity": [r"o\(1\)", r"constant time", r"o\(n\)", r"linear time"],
        "fifo": [r"\bfifo\b", r"first[\s-]in[\s,]+first[\s-]out", r"first arrived.*first served"],
        "enqueue": [r"\benqueue\b", r"add.*rear", r"insert.*rear", r"add.*tail", r"add.*back"],
        "dequeue": [r"\bdequeue\b", r"remove.*front", r"delete.*front", r"remove.*head"],
        "front_rear_pointers": [r"front.*rear", r"head.*tail", r"pointers?"],
        "circular_queue": [r"circular", r"modulo", r"%\s*capacity", r"wraparound", r"false overflow"],
        "monotonic_stack": [r"monotonic", r"next greater", r"increasing.*decreasing"],
        "queue_using_stacks": [r"two stacks?", r"in_stack.*out_stack", r"input.*output", r"amortized"],
    }

    # Patterns indicating reasoning & justification
    REASONING_PATTERNS = [
        r"\bbecause\b", r"\bsince\b", r"\btherefore\b", r"\bas a result\b",
        r"\bdue to\b", r"\bmeaning that\b", r"\bin order to\b", r"\bwhich prevents\b",
        r"\bso that\b", r"\bwhy\b", r"\breason\b"
    ]

    # Specific misconception detector patterns
    MISCONCEPTION_PATTERNS = {
        "Stack operates on First In, First Out (FIFO)": [
            r"stack.*(fifo|first in first out)",
            r"first in first out.*stack"
        ],
        "Pop removes the oldest or bottom element": [
            r"pop.*(oldest|bottom|first added)",
            r"removes? (the )?(oldest|bottom|first) element"
        ],
        "Elements can be added or removed from any arbitrary index in a standard stack": [
            r"(add|remove|insert|access).*(any|arbitrary|middle) (index|position|element)"
        ],
        "Peek modifies the stack by removing the top element": [
            r"peek.*removes?",
            r"peek.*deletes?"
        ],
        "Popping an empty stack returns the last pushed item": [
            r"pop.*empty.*returns? (the )?last"
        ],
        "Breadth-first search (BFS) uses a stack by default": [
            r"bfs.*uses? (a )?stack",
            r"breadth-first.*uses? (a )?stack"
        ],
        "The call stack operates as First In, First Out": [
            r"call stack.*(fifo|first in first out)"
        ],
        "Push or pop in a stack requires O(n) linear time because elements must shift": [
            r"(push|pop).*requires? o\(n\)",
            r"(push|pop).*shifts? (all )?elements"
        ],
        "Array and linked list implementations have identical memory overhead": [
            r"(array|linked list).*identical memory"
        ],
        "A nested while-loop inside the traversal automatically makes the algorithm O(n^2)": [
            r"nested (while|loop).*makes? (it |the algorithm )?o\(n\^2\)",
            r"monotonic.*is o\(n\^2\)"
        ],
        "A monotonic stack requires sorting the entire array first": [
            r"monotonic.*requires? sorting",
            r"sort the array first"
        ],
        "Queue operates on Last In, First Out (LIFO)": [
            r"queue.*(lifo|last in first out)"
        ],
        "Enqueue and dequeue happen at the same end of the data structure": [
            r"(enqueue|dequeue).*same end",
            r"insert.*remove.*same end"
        ],
        "Rear pointer points to the next item to be removed": [
            r"rear.*(points? to.*removed|removes?)"
        ],
        "Dequeuing from an empty queue returns the front element from a previous session": [
            r"dequeue.*empty.*returns?.*previous"
        ],
        "Linear queues automatically shift all elements on every dequeue without performance cost": [
            r"linear queue.*shifts?.*without (cost|overhead)"
        ],
        "Circular queues require a circular doubly linked list": [
            r"circular queue.*requires? (a )?circular doubly"
        ],
        "Depth-First Search (DFS) relies on a queue": [
            r"dfs.*relies on (a )?queue",
            r"depth-first.*uses? (a )?queue"
        ],
        "LIFO order is needed for fair printer job spooling": [
            r"printer.*(lifo|last in first out)"
        ],
        "Transferring elements back and forth on every single dequeue or enqueue is required": [
            r"transfer.*back and forth.*every (single )?(dequeue|enqueue)"
        ],
        "The worst-case O(n) transfer means the average/amortized performance is also O(n)": [
            r"(amortized|average).*performance is (also )?o\(n\)"
        ],
    }

    def evaluate(self, question: Dict[str, Any], answer: str) -> EvaluationResult:
        """
        Evaluates a student's answer for a given question using the 10-point rubric.
        """
        cleaned_answer = (answer or "").strip()

        # Handle empty answer
        if not cleaned_answer:
            return self._handle_empty_answer(question)

        lower_answer = cleaned_answer.lower()

        # 1. Detect critical misconceptions
        detected_misconceptions = self._detect_misconceptions(question, lower_answer)

        # 2. Evaluate expected points coverage
        expected_points = question.get("expected_points", [])
        matched_points, missing_points = self._match_expected_points(expected_points, lower_answer)

        # 3. Calculate rubric components
        coverage_ratio = len(matched_points) / max(len(expected_points), 1)

        # Technical correctness (0-4)
        if detected_misconceptions:
            tc = max(0, min(1, int(coverage_ratio * 4) - 1))
        else:
            tc = int(round(coverage_ratio * 4))

        # Key concepts (0-3)
        concepts = question.get("concepts", [])
        matched_concepts = self._match_concepts(concepts, lower_answer)
        concept_ratio = len(matched_concepts) / max(len(concepts), 1)
        if detected_misconceptions:
            kc = min(1, int(round(concept_ratio * 3)))
        else:
            kc = int(round(concept_ratio * 3))

        # Reasoning (0-2)
        if detected_misconceptions:
            re_pt = 0
        else:
            has_reasoning = any(re.search(pat, lower_answer) for pat in self.REASONING_PATTERNS)
            re_pt = 0
            if has_reasoning and len(matched_points) >= 1:
                re_pt = 2 if len(matched_points) >= 2 else 1
            elif len(matched_points) >= 2:
                re_pt = 1

        # Clarity (0-1)
        # 1 if student writes at least one complete sentence or clear explanation
        cl = 1 if len(cleaned_answer.split()) >= 6 else 0

        # Overall score
        score = tc + kc + re_pt + cl
        if detected_misconceptions:
            score = max(0, min(4, score))
        else:
            score = max(0, min(10, score))

        # Ensure sum matches score
        sum_components = tc + kc + re_pt + cl
        if score != sum_components:
            tc = max(0, min(4, score - (kc + re_pt + cl)))
            score = tc + kc + re_pt + cl

        # 4. Determine recommended action per PRD 10.2
        if detected_misconceptions or score <= 4:
            recommended_action = "scaffold_hint"
            action_desc = "Let's strengthen the fundamentals with a focused follow-up."
        elif missing_points or score <= 7:
            recommended_action = "targeted_follow_up"
            action_desc = "Your answer is partly correct. Let's revisit one important concept."
        else:
            recommended_action = "progress"
            action_desc = "Good explanation. Let's move to the next concept."

        # 5. Generate actionable feedback
        feedback = self._build_feedback(
            score=score,
            matched_points=matched_points,
            missing_points=missing_points,
            misconceptions=detected_misconceptions,
            action_desc=action_desc
        )

        confidence = "high" if (score >= 8 or score <= 3 or detected_misconceptions) else "medium"

        result: EvaluationResult = {
            "score": score,
            "score_breakdown": {
                "technical_correctness": tc,
                "key_concepts": kc,
                "reasoning": re_pt,
                "clarity": cl,
            },
            "correct_points": matched_points,
            "missing_concepts": missing_points,
            "misconceptions": detected_misconceptions,
            "feedback": feedback,
            "confidence": confidence,
            "recommended_action": recommended_action,
            "evaluation_provider": "local",
        }

        # Validate result schema before returning
        validate_evaluation_result(result)
        return result

    def _handle_empty_answer(self, question: Dict[str, Any]) -> EvaluationResult:
        """Constructs a validated zero-score result for empty submissions."""
        return {
            "score": 0,
            "score_breakdown": {
                "technical_correctness": 0,
                "key_concepts": 0,
                "reasoning": 0,
                "clarity": 0,
            },
            "correct_points": [],
            "missing_concepts": list(question.get("expected_points", [])),
            "misconceptions": [],
            "feedback": "Write an answer before submitting. Explain the key concepts and reasoning step by step.",
            "confidence": "high",
            "recommended_action": "scaffold_hint",
            "evaluation_provider": "local",
        }

    def _detect_misconceptions(self, question: Dict[str, Any], lower_answer: str) -> List[str]:
        """Checks student answer for known critical misconceptions for the question."""
        detected = []
        for mis in question.get("critical_misconceptions", []):
            patterns = self.MISCONCEPTION_PATTERNS.get(mis, [])
            if patterns:
                for pat in patterns:
                    if re.search(pat, lower_answer):
                        detected.append(mis)
                        break
            else:
                # Generic fallback check if words from misconception appear in invalid assertion
                mis_words = [w for w in mis.lower().split() if len(w) > 3]
                if mis_words and sum(1 for w in mis_words if w in lower_answer) >= len(mis_words) * 0.75:
                    detected.append(mis)
        return detected

    def _match_expected_points(self, expected_points: List[str], lower_answer: str) -> tuple[List[str], List[str]]:
        """Matches student answer text against expected answer points."""
        matched = []
        missing = []

        for pt in expected_points:
            pt_lower = pt.lower()
            # Extract key technical tokens from expected point
            tokens = [t for t in re.findall(r"\b[a-z_0-9\(\)]+\b", pt_lower) if len(t) > 2 and t not in {"the", "and", "for", "with", "from", "that"}]
            if not tokens:
                matched.append(pt)
                continue

            # Check if majority of core tokens or conceptual phrases match
            matched_count = sum(1 for t in tokens if t in lower_answer)
            ratio = matched_count / len(tokens)

            # Check conceptual synonym match
            has_concept_synonym = False
            for concept, synonyms in self.CONCEPT_SYNONYMS.items():
                if concept in pt_lower or any(re.search(syn, pt_lower) for syn in synonyms):
                    if any(re.search(syn, lower_answer) for syn in synonyms):
                        has_concept_synonym = True
                        break

            if ratio >= 0.45 or has_concept_synonym:
                matched.append(pt)
            else:
                missing.append(pt)

        return matched, missing

    def _match_concepts(self, concepts: List[str], lower_answer: str) -> List[str]:
        """Matches topic concept tags against answer text."""
        matched = []
        for c in concepts:
            c_lower = c.lower()
            synonyms = self.CONCEPT_SYNONYMS.get(c_lower, [re.escape(c_lower)])
            if any(re.search(syn, lower_answer) for syn in synonyms) or c_lower in lower_answer:
                matched.append(c)
        return matched

    def _build_feedback(
        self,
        score: int,
        matched_points: List[str],
        missing_points: List[str],
        misconceptions: List[str],
        action_desc: str
    ) -> str:
        """Constructs clear, beginner-friendly feedback text."""
        parts = []

        if score >= 8:
            parts.append(f"Strong response ({score}/10)!")
        elif score >= 5:
            parts.append(f"Good effort ({score}/10) with partial understanding.")
        else:
            parts.append(f"Foundational practice needed ({score}/10).")

        if matched_points:
            parts.append(f"Correctly explained: {'; '.join(matched_points)}.")

        if misconceptions:
            parts.append(f"Important correction: {'; '.join(misconceptions)}.")

        if missing_points:
            parts.append(f"Missing concept: {missing_points[0]}.")

        parts.append(action_desc)
        return " ".join(parts)


def evaluate_answer(
    question: Dict[str, Any],
    answer: str,
    provider: str = "local"
) -> EvaluationResult:
    """
    Unified public interface for evaluating an answer per TRD Section 8.1.
    Currently routes to LocalEvaluator (default offline).
    """
    if provider == "local":
        evaluator = LocalEvaluator()
        return evaluator.evaluate(question, answer)
    elif provider == "bedrock":
        # Bedrock evaluator is optional and deferred to Phase 8 per TRD Section 20
        # Safe fallback to local evaluator if Bedrock is requested before configured
        evaluator = LocalEvaluator()
        result = evaluator.evaluate(question, answer)
        result["evaluation_provider"] = "local"
        return result
    else:
        raise ValueError(f"Unknown evaluation provider: '{provider}'. Supported: {ALLOWED_PROVIDERS}")
