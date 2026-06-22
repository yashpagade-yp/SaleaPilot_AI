"""Response schemas for feedback-related API operations."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class FeedbackResponse(BaseModel):
    """Response payload for one training-session feedback record."""

    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: str = Field(..., description="Feedback record identifier.")
    training_session_id: str = Field(..., description="Training session identifier.")
    user_id: str = Field(..., description="Salesperson user identifier.")
    scenario_id: str = Field(..., description="Scenario identifier.")
    summary: str = Field(..., description="High-level coaching summary.")
    strengths: list[str] = Field(..., description="Observed strengths in the session.")
    improvement_areas: list[str] = Field(
        ...,
        description="Areas where the salesperson should improve.",
    )
    objection_handling_score: float = Field(..., description="Objection handling score.")
    confidence_score: float = Field(..., description="Confidence score.")
    clarity_score: float = Field(..., description="Communication clarity score.")
    rapport_score: float = Field(..., description="Rapport-building score.")
    closing_score: float = Field(..., description="Closing effectiveness score.")
    recommendations: list[str] = Field(
        ...,
        description="Actionable recommendations for future practice.",
    )
    raw_feedback_payload: dict[str, Any] | None = Field(
        default=None,
        description="Optional raw feedback payload for traceability.",
    )
    created_at: datetime = Field(..., description="UTC timestamp when feedback was created.")
