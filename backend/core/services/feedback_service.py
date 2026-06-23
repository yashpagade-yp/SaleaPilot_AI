"""Service layer for generating structured coaching feedback."""

from __future__ import annotations

import math
import re
from typing import Any

from commons.logger import logger

logging = logger(__name__)

FILLER_WORDS = {"um", "uh", "like", "actually", "basically"}
QUESTION_WORDS = {"what", "how", "why", "when", "where", "who"}
RAPPORT_WORDS = {"understand", "help", "thanks", "appreciate", "great", "sure"}
CLOSING_WORDS = {
    "next step",
    "follow up",
    "schedule",
    "demo",
    "trial",
    "meeting",
    "calendar",
}
OBJECTION_WORDS = {
    "busy",
    "not interested",
    "already using",
    "price",
    "cost",
    "later",
    "send me",
    "too expensive",
}


class FeedbackGenerationService:
    """Service for transcript-driven coaching feedback generation."""

    def normalize_transcript(self, transcript_payload: Any) -> str:
        """Flatten a transcript payload into one readable text block.

        Args:
            transcript_payload (Any): Raw transcript payload from Eigi.

        Returns:
            str: Plain-text transcript representation.
        """
        logging.info("Executing FeedbackGenerationService.normalize_transcript")
        if transcript_payload is None:
            return ""

        if isinstance(transcript_payload, str):
            return transcript_payload.strip()

        lines: list[str] = []

        def walk(value: Any) -> None:
            if value is None:
                return
            if isinstance(value, str):
                cleaned = value.strip()
                if cleaned:
                    lines.append(cleaned)
                return
            if isinstance(value, dict):
                speaker = value.get("speaker") or value.get("role") or value.get("name")
                text = value.get("text") or value.get("content") or value.get("message")
                if isinstance(text, str) and text.strip():
                    prefix = f"{speaker}: " if speaker else ""
                    lines.append(f"{prefix}{text.strip()}")
                    return
                for nested_value in value.values():
                    walk(nested_value)
                return
            if isinstance(value, list):
                for item in value:
                    walk(item)

        walk(transcript_payload)
        return "\n".join(lines).strip()

    def _score_range(self, value: float) -> float:
        """Clamp a floating-point score into the 0-10 range.

        Args:
            value (float): Candidate score.

        Returns:
            float: Rounded score between 0 and 10.
        """
        return round(max(0.0, min(10.0, value)), 1)

    def generate_feedback(
        self,
        *,
        transcript: str,
        scenario_title: str,
        conversation_analysis: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Generate structured coaching feedback from transcript content.

        Args:
            transcript (str): Normalized transcript text.
            scenario_title (str): Human-readable scenario title.
            conversation_analysis (dict[str, Any] | None): Optional analysis payload.

        Returns:
            dict[str, Any]: Structured feedback payload matching the Feedback model.
        """
        logging.info("Executing FeedbackGenerationService.generate_feedback")
        conversation_analysis = conversation_analysis or {}

        lowered = transcript.lower()
        words = re.findall(r"\b[\w']+\b", lowered)
        word_count = len(words)
        question_count = transcript.count("?")
        filler_count = sum(words.count(word) for word in FILLER_WORDS)
        rapport_count = sum(words.count(word) for word in RAPPORT_WORDS)
        question_word_hits = sum(words.count(word) for word in QUESTION_WORDS)
        closing_hits = sum(lowered.count(phrase) for phrase in CLOSING_WORDS)
        objection_hits = sum(lowered.count(phrase) for phrase in OBJECTION_WORDS)

        clarity_penalty = filler_count * 0.7
        clarity_bonus = min(question_count + question_word_hits, 4) * 0.3
        clarity_score = self._score_range(7.0 + clarity_bonus - clarity_penalty)

        rapport_score = self._score_range(5.5 + (rapport_count * 0.8) + min(question_count, 3) * 0.4)
        objection_score = self._score_range(4.5 + min(objection_hits, 4) * 1.1 + min(question_count, 4) * 0.5)
        confidence_score = self._score_range(6.0 + min(word_count / 120, 2.5) - min(filler_count, 4) * 0.4)
        closing_score = self._score_range(4.5 + closing_hits * 1.8)

        sentence_count = max(1, len(re.findall(r"[.!?]", transcript)))
        average_sentence_length = word_count / sentence_count
        clarity_adjustment = 0.7 if 8 <= average_sentence_length <= 24 else -0.3
        clarity_score = self._score_range(clarity_score + clarity_adjustment)

        strengths: list[str] = []
        improvement_areas: list[str] = []
        recommendations: list[str] = []

        if question_count >= 3 or question_word_hits >= 3:
            strengths.append("Asked discovery-style questions to understand the customer.")
        else:
            improvement_areas.append("Use more discovery questions to uncover customer needs.")
            recommendations.append("Prepare 3-5 open-ended discovery questions before the next call.")

        if rapport_count >= 2:
            strengths.append("Showed rapport-building language during the conversation.")
        else:
            improvement_areas.append("Build more rapport and empathy early in the call.")
            recommendations.append("Acknowledge the customer's situation before pitching the product.")

        if objection_hits >= 1:
            strengths.append("Engaged with customer objections instead of ignoring them.")
        else:
            improvement_areas.append("Practice responding to objections more directly.")
            recommendations.append("Rehearse responses for price, timing, and existing-tool objections.")

        if closing_hits >= 1:
            strengths.append("Moved the conversation toward a concrete next step.")
        else:
            improvement_areas.append("End the call with a clearer next step or close.")
            recommendations.append("Close each practice call with a demo, follow-up, or calendar ask.")

        if filler_count >= 4:
            improvement_areas.append("Reduce filler words to sound more concise and confident.")
            recommendations.append("Pause briefly instead of filling silence with 'um' or 'uh'.")
        else:
            strengths.append("Kept delivery relatively clean with limited filler language.")

        if not strengths:
            strengths.append("Stayed engaged throughout the roleplay and maintained the conversation flow.")
        if not improvement_areas:
            improvement_areas.append("Refine the call structure to improve consistency across roleplays.")
        if not recommendations:
            recommendations.append("Review the transcript and highlight one objection and one closing moment to improve.")

        average_score = self._score_range(
            (objection_score + confidence_score + clarity_score + rapport_score + closing_score) / 5
        )
        summary = (
            f"This {scenario_title} practice session showed an overall coaching score of {average_score}/10. "
            f"The call included {question_count} direct questions and {closing_hits} clear next-step moments."
        )

        if conversation_analysis:
            recommendations.append("Compare this transcript with Eigi's analysis to validate coaching themes.")

        return {
            "summary": summary,
            "strengths": strengths[:4],
            "improvement_areas": improvement_areas[:4],
            "objection_handling_score": objection_score,
            "confidence_score": confidence_score,
            "clarity_score": clarity_score,
            "rapport_score": rapport_score,
            "closing_score": closing_score,
            "recommendations": recommendations[:4],
            "raw_feedback_payload": {
                "word_count": word_count,
                "question_count": question_count,
                "filler_count": filler_count,
                "rapport_count": rapport_count,
                "closing_hits": closing_hits,
                "objection_hits": objection_hits,
                "conversation_analysis": conversation_analysis,
            },
        }
