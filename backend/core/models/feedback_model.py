"""Feedback model definitions for post-session coaching output."""

from datetime import datetime, timezone
from typing import Any

from odmantic import Field, Model
from odmantic.config import ODMConfigDict

def utc_now() -> datetime:
    """Return the current UTC datetime.

    This helper keeps timestamp defaults consistent across feedback records.

    Returns:
        datetime: Current UTC-aware datetime.
    """
    return datetime.now(timezone.utc)


class Feedback(Model):
    """Persisted coaching feedback generated for one training session.

    Stores structured strengths, improvement areas, and scores so the frontend
    can present clear coaching insights to the salesperson after a session.
    """

    training_session_id: str = Field(
        ...,
        unique=True,
        description="Training session identifier associated with this feedback.",
    )
    user_id: str = Field(
        ...,
        description="User identifier of the salesperson receiving the feedback.",
    )
    scenario_id: str = Field(
        ...,
        description="Scenario identifier associated with the completed session.",
    )
    summary: str = Field(
        ...,
        min_length=10,
        description="High-level coaching summary for the session.",
    )
    strengths: list[str] = Field(
        default_factory=list,
        description="List of positive behaviors observed during the session.",
    )
    improvement_areas: list[str] = Field(
        default_factory=list,
        description="List of areas the salesperson should improve.",
    )
    objection_handling_score: float = Field(
        ...,
        ge=0,
        le=10,
        description="Score representing objection handling performance.",
    )
    confidence_score: float = Field(
        ...,
        ge=0,
        le=10,
        description="Score representing confidence during the session.",
    )
    clarity_score: float = Field(
        ...,
        ge=0,
        le=10,
        description="Score representing communication clarity.",
    )
    rapport_score: float = Field(
        ...,
        ge=0,
        le=10,
        description="Score representing rapport-building quality.",
    )
    closing_score: float = Field(
        ...,
        ge=0,
        le=10,
        description="Score representing closing effectiveness.",
    )
    recommendations: list[str] = Field(
        default_factory=list,
        description="Practical recommendations for the next practice session.",
    )
    raw_feedback_payload: dict[str, Any] | None = Field(
        default=None,
        description="Optional raw feedback payload retained for traceability.",
    )
    created_at: datetime = Field(
        default_factory=utc_now,
        description="UTC timestamp when the feedback record was created.",
    )
    updated_at: datetime = Field(
        default_factory=utc_now,
        description="UTC timestamp when the feedback record was last updated.",
    )

    model_config = ODMConfigDict(
        collection="feedback",
        extra="forbid",
    )
