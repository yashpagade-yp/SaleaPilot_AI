"""Request schemas for scenario-related API operations."""

from pydantic import BaseModel, ConfigDict, Field


class ScenarioListRequest(BaseModel):
    """Request schema for listing scenarios with optional active filtering."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    active_only: bool = Field(
        default=True,
        description="Whether only active scenarios should be returned.",
    )

