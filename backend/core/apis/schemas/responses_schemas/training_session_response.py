"""Response schemas for training-session-related API operations."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from core.models.scenario_model import ScenarioKey
from core.models.training_session_model import TrainingSessionStatus


class TrainingSessionResponse(BaseModel):
    """Response payload representing a training session record."""

    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: str = Field(..., description="Training session identifier.")
    user_id: str = Field(..., description="Salesperson user identifier.")
    scenario_id: str = Field(..., description="Scenario identifier.")
    scenario_key: ScenarioKey = Field(..., description="Selected scenario key.")
    agent_id: str = Field(..., description="Mapped Eigi agent identifier.")
    status: TrainingSessionStatus = Field(..., description="Training session status.")
    conversation_id: str | None = Field(
        default=None,
        description="Eigi conversation identifier, when available.",
    )
    started_at: datetime | None = Field(
        default=None,
        description="UTC timestamp when the session started, if available.",
    )
    ended_at: datetime | None = Field(
        default=None,
        description="UTC timestamp when the session ended, if available.",
    )


class StartTrainingSessionResponse(BaseModel):
    """Response payload after creating a new training session."""

    model_config = ConfigDict(extra="forbid")

    session_id: str = Field(..., description="Created training session identifier.")
    eigi_record_id: str | None = Field(
        default=None,
        description="Internal Eigi Daily session identifier.",
    )
    conversation_id: str | None = Field(
        default=None,
        description="Eigi conversation identifier.",
    )
    daily_room: str | None = Field(
        default=None,
        description="Daily room URL for the frontend join flow.",
    )
    daily_token: str | None = Field(
        default=None,
        description="Daily token used to join the room securely.",
    )
    status: TrainingSessionStatus = Field(
        ...,
        description="Initial status of the training session.",
    )

