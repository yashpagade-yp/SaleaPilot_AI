"""Response schemas for invitation-related API operations."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from core.models.invitation_model import InvitationStatus
from core.models.user_model import UserRole


class InvitationResponse(BaseModel):
    """Response payload representing an invitation record."""

    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: str = Field(..., description="Invitation identifier.")
    email: EmailStr = Field(..., description="Email address receiving the invitation.")
    role: UserRole = Field(..., description="Role granted by the invitation.")
    status: InvitationStatus = Field(..., description="Current invitation status.")
    invited_by: str = Field(..., description="Admin user identifier who sent the invite.")
    expires_at: datetime = Field(..., description="UTC timestamp when the invite expires.")
    accepted_at: datetime | None = Field(
        default=None,
        description="UTC timestamp when the invite was accepted, if applicable.",
    )


class InvitationAcceptResponse(BaseModel):
    """Response payload after a salesperson accepts an invitation."""

    model_config = ConfigDict(extra="forbid")

    message: str = Field(..., description="Human-readable invitation acceptance result.")
    user_id: str = Field(..., description="Created or activated salesperson user identifier.")

