"""
EduAgent Interview Coach — Final Report Generator & Study Analytics
===================================================================

Generates comprehensive, structured post-interview performance summaries,
separating verified demonstrated strengths from unresolved gaps, and produces
prioritized DSA revision recommendations per PRD FR-16 and TRD Section 13.1.
"""

from typing import Any, Dict, List, Optional, Union

from interview_engine import InterviewSession


class ReportGenerator:
    """
    Synthesizes session attempt records and concept mastery state into an
    actionable evaluation report and markdown summary.
    """

    DISCLAIMER_TEXT = (
        "This report provides practice feedback to support technical interview preparation. "
        "It is designed for self-assessment and does not guarantee specific interview or hiring outcomes."
    )

    RECOMMENDATION_CATALOG = {
        "underflow": (
            "Practice empty-collection edge cases: Always verify that size > 0 before calling pop() "
            "or dequeue() to prevent underflow exceptions."
        ),
        "overflow": (
            "Review bounded capacity handling: Ensure fixed-size arrays check size == capacity "
            "before pushing or enqueuing to prevent overflow."
        ),
        "modulo": (
            "Master circular queue index calculations: Use modular arithmetic ((index + 1) % capacity) "
            "for smooth pointer wraparound without element shifting."
        ),
        "circular": (
            "Study circular queue pointer mechanics: Differentiate full vs empty conditions "
            "(e.g., maintaining an explicit count variable or keeping one slot empty)."
        ),
        "two stacks": (
            "Practice implementing a queue with two stacks: Understand why transferring elements from "
            "in_stack to out_stack yields amortized O(1) dequeue operations."
        ),
        "monotonic": (
            "Explore monotonic stack problems (e.g., Next Greater Element or Daily Temperatures) "
            "to understand how pruning elements achieves linear O(n) total runtime."
        ),
        "complexity": (
            "Review amortized vs worst-case analysis: While dynamic array resizing takes O(n) rarely, "
            "its amortized cost per push remains O(1)."
        ),
        "lifo": (
            "Reinforce the LIFO principle: Elements are added and removed from the same end (the top). "
            "Ideal for recursion, call stacks, and parenthesis matching."
        ),
        "fifo": (
            "Reinforce the FIFO principle: Elements enter at the rear and exit from the front. "
            "Essential for breadth-first search (BFS) and asynchronous task scheduling."
        ),
    }

    @classmethod
    def generate_report(
        cls, session: Union[InterviewSession, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Builds the complete final evaluation report dictionary.
        Accepts either an InterviewSession instance or its dictionary representation.
        """
        if isinstance(session, InterviewSession):
            data = session.to_dict()
            total_score = session.total_score
            avg_score = session.average_score
        elif isinstance(session, dict):
            data = session
            attempts = data.get("attempts", [])
            valid_attempts = [
                a for a in attempts
                if isinstance(a.get("evaluation"), dict) and "score" in a["evaluation"]
            ]
            total_score = sum(a["evaluation"]["score"] for a in valid_attempts)
            avg_score = (
                round(total_score / len(valid_attempts), 1) if valid_attempts else 0.0
            )
        else:
            raise ValueError(f"Expected InterviewSession or dict, got {type(session).__name__}")

        attempts = data.get("attempts", [])
        attempts_count = len(attempts)
        max_possible = attempts_count * 10
        percentage = round((total_score / max_possible) * 100, 1) if max_possible > 0 else 0.0

        # Performance Tier classification
        if attempts_count == 0:
            tier = "Incomplete"
            tier_summary = "No questions completed in this session."
        elif percentage >= 80.0:
            tier = "Proficient"
            tier_summary = "Strong conceptual mastery of Stacks and Queues with sound technical reasoning."
        elif percentage >= 50.0:
            tier = "Developing"
            tier_summary = "Good foundational knowledge with some missing operation mechanics or edge cases."
        else:
            tier = "Foundational"
            tier_summary = "Core concepts need reinforcement, particularly around basic definitions and operations."

        demonstrated = sorted(list(data.get("demonstrated_concepts", [])))
        unresolved = sorted(list(data.get("unresolved_concepts", [])))

        # Extract specific misconceptions from attempts
        misconceptions = []
        for att in attempts:
            eval_dict = att.get("evaluation", {})
            for m in eval_dict.get("misconceptions", []):
                if m not in misconceptions:
                    misconceptions.append(m)

        recommendations = cls._generate_recommendations(unresolved, misconceptions, tier)

        # Question attempt summaries
        question_summaries = []
        for idx, att in enumerate(attempts, 1):
            eval_info = att.get("evaluation", {})
            question_summaries.append({
                "number": idx,
                "question_id": att.get("question_id", "unknown"),
                "question_text": att.get("question_text", ""),
                "topic": att.get("topic", "DSA"),
                "difficulty": att.get("difficulty", "medium"),
                "score": eval_info.get("score", 0),
                "hint_used": att.get("hint_used", False),
                "feedback": eval_info.get("feedback", ""),
            })

        return {
            "session_id": data.get("session_id", "unknown"),
            "created_at": data.get("created_at", ""),
            "evaluation_mode": data.get("evaluation_provider", "local"),
            "attempts_count": attempts_count,
            "total_score": total_score,
            "max_possible_score": max_possible,
            "average_score": avg_score,
            "percentage": percentage,
            "performance_tier": tier,
            "tier_summary": tier_summary,
            "hints_used": data.get("hints_used_count", 0),
            "demonstrated_concepts": demonstrated,
            "unresolved_concepts": unresolved,
            "misconceptions_detected": misconceptions,
            "recommendations": recommendations,
            "question_summaries": question_summaries,
            "disclaimer": cls.DISCLAIMER_TEXT,
        }

    @classmethod
    def generate_markdown_report(cls, report: Dict[str, Any]) -> str:
        """
        Formats the report dictionary as clean, readable Markdown for UI or export.
        """
        lines = [
            f"# EduAgent Interview Performance Report",
            f"**Session ID:** `{report['session_id']}`  |  **Evaluation Mode:** `{report['evaluation_mode']}`",
            "",
            "## 1. Overall Performance",
            f"- **Performance Tier:** **{report['performance_tier']}**",
            f"- **Score:** **{report['total_score']} / {report['max_possible_score']}** ({report['percentage']}%)",
            f"- **Average Score per Question:** **{report['average_score']} / 10**",
            f"- **Questions Completed:** {report['attempts_count']}",
            f"- **Hints Requested:** {report['hints_used']}",
            f"- **Summary:** {report['tier_summary']}",
            "",
            "## 2. Demonstrated Strengths",
        ]

        if report["demonstrated_concepts"]:
            for concept in report["demonstrated_concepts"]:
                lines.append(f"- :white_check_mark: **{concept}**")
        else:
            lines.append("- *No concepts were fully demonstrated in this session.*")

        lines.append("")
        lines.append("## 3. Areas for Practice")

        if report["unresolved_concepts"]:
            for concept in report["unresolved_concepts"]:
                lines.append(f"- :mag: {concept}")
        else:
            lines.append("- :sparkles: *No outstanding concept gaps were recorded.*")

        if report["misconceptions_detected"]:
            lines.append("")
            lines.append("### Misconceptions Detected")
            for m in report["misconceptions_detected"]:
                lines.append(f"- :warning: **{m}**")

        lines.append("")
        lines.append("## 4. Priority Revision Recommendations")
        for idx, rec in enumerate(report["recommendations"], 1):
            lines.append(f"{idx}. {rec}")

        lines.append("")
        lines.append("---")
        lines.append(f"> *{report['disclaimer']}*")

        return "\n".join(lines)

    @classmethod
    def _generate_recommendations(
        cls,
        unresolved_concepts: List[str],
        misconceptions: List[str],
        tier: str,
    ) -> List[str]:
        """Maps unresolved concepts and misconceptions to prioritized study recommendations."""
        recommendations: List[str] = []
        combined_text = " ".join(unresolved_concepts + misconceptions).lower()

        for keyword, advice in cls.RECOMMENDATION_CATALOG.items():
            if keyword in combined_text:
                if advice not in recommendations:
                    recommendations.append(advice)

        # Ensure general recommendations if few specific ones were matched
        if len(recommendations) < 2:
            if tier == "Foundational":
                recommendations.append(
                    "Start by diagramming Stacks and Queues on paper: Draw push/pop from the top for Stacks, "
                    "and enqueue at the rear / dequeue from the front for Queues."
                )
                recommendations.append(
                    "Review array-based vs linked-list implementations to understand how pointer movement works."
                )
            else:
                recommendations.append(
                    "Practice tracing real-world interview applications: Balanced parentheses using a stack, "
                    "and breadth-first search (BFS) level-order traversal using a queue."
                )
                recommendations.append(
                    "Focus on explaining time complexity tradeoffs aloud: Why linked list vs dynamic array "
                    "both achieve O(1) amortized stack operations."
                )

        return recommendations[:5]
