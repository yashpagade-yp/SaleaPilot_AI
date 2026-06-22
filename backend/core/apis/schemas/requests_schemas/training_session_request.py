"""Request schemas for training-session-related API operations."""

from pydantic import BaseModel, ConfigDict, Field

from core.models.scenario_model import ScenarioKey


class StartTrainingSessionRequest(BaseModel):
    """Request payload for starting a new salesperson training session."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    scenario_key: ScenarioKey = Field(
        ...,
        description="Selected scenario key for the training session.",
    )

