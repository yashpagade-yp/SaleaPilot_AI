"""Request schemas for admin management API operations."""

from pydantic import BaseModel, ConfigDict, Field


class SalespersonStatusUpdateRequest(BaseModel):
    """Request payload for changing salesperson activation status."""

    model_config = ConfigDict(extra="forbid")

    is_active: bool = Field(
        ...,
        description="Whether the salesperson account should be active after the update.",
    )
