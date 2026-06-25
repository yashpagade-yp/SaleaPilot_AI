"""Response schemas for scenario-related API operations."""

from pydantic import BaseModel, ConfigDict, Field

from core.models.scenario_model import ScenarioKey


class ScenarioResponse(BaseModel):
    """Response payload for one training scenario."""

    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: str = Field(..., description="Scenario identifier.")
    key: ScenarioKey = Field(..., description="Scenario key.")
    title: str = Field(..., description="Display title of the scenario.")
    description: str = Field(..., description="Short description of the scenario.")
    agent_id: str = Field(..., description="Eigi agent identifier mapped to the scenario.")
    is_active: bool = Field(..., description="Whether the scenario is active.")
    sort_order: int = Field(..., description="Display order for scenario listing.")


class ScenarioListResponse(BaseModel):
    """Response payload for listing training scenarios."""

    model_config = ConfigDict(extra="forbid")

    items: list[ScenarioResponse] = Field(..., description="Available training scenarios.")

