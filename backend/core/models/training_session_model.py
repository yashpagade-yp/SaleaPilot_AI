"""Training session model definitions for salesperson practice calls."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional

from odmantic import Field, Model
from odmantic.config import ODMConfigDict

from core.models.scenario_model import ScenarioKey


def utc_now() -> datetime:
    """Return the current UTC datetime.

    This helper keeps timestamp defaults consistent across training sessions.

    Returns:
        datetime: Current UTC-aware datetime.
    """
    return datetime.now(timezone.utc)


class TrainingSessionStatus(str, Enum):
    """Lifecycle states for a salesperson training session."""

    CREATED = "CREATED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class TrainingSession(Model):
    """Persisted practice session started by a salesperson.

    Stores the selected scenario, mapped Eigi agent, Daily connection details,
    and session-level metadata needed to join and track the voice call.
    """

    user_id: str = Field(
        ...,
        description="User identifier of the salesperson starting the session.",
    )
    scenario_id: str = Field(
        ...,
        description="Scenario identifier selected for the session.",
    )
    scenario_key: ScenarioKey = Field(
        ...,
        description="Scenario key selected for the session.",
    )
    agent_id: str = Field(
        ...,
        min_length=8,
        description="Eigi agent identifier used for this session.",
    )
    status: TrainingSessionStatus = Field(
        default=TrainingSessionStatus.CREATED,
        description="Current lifecycle state of the training session.",
    )
    conversation_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Salesperson name used inside conversation metadata.",
    )
    conversation_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Dynamic metadata sent with the Eigi Daily conversation payload.",
    )
    eigi_record_id: Optional[str] = Field(
        default=None,
        description="Internal Eigi record identifier returned by the Daily API.",
    )
    conversation_id: Optional[str] = Field(
        default=None,
        description="Eigi conversation identifier for history and transcript lookup.",
    )
    daily_room: Optional[str] = Field(
        default=None,
        description="Daily room URL returned for the browser call join flow.",
    )
    daily_token: Optional[str] = Field(
        default=None,
        description="Daily token returned for authenticated room access.",
    )
    started_at: Optional[datetime] = Field(
        default=None,
        description="UTC timestamp when the voice session actually started.",
    )
    ended_at: Optional[datetime] = Field(
        default=None,
        description="UTC timestamp when the voice session ended.",
    )
    duration_seconds: Optional[int] = Field(
        default=None,
        ge=0,
        description="Computed session duration in seconds, when available.",
    )
    created_at: datetime = Field(
        default_factory=utc_now,
        description="UTC timestamp when the record was created.",
    )
    updated_at: datetime = Field(
        default_factory=utc_now,
        description="UTC timestamp when the record was last updated.",
    )

    model_config = ODMConfigDict(
        collection="training_sessions",
        extra="forbid",
    )
