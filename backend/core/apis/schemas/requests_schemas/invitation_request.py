"""Request schemas for invitation-related API operations."""

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class SendInvitationRequest(BaseModel):
    """Request payload for sending an invitation to a salesperson."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    email: EmailStr = Field(
        ...,
        description="Salesperson email address that should receive the invitation.",
    )
    first_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=50,
        description="Optional first name of the invited salesperson.",
    )
    last_name: str | None = Field(
        default=None,
        min_length=2,
        max_length=50,
        description="Optional last name of the invited salesperson.",
    )


class AcceptInvitationRequest(BaseModel):
    """Request payload for acknowledging an invitation token."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    token: str = Field(
        ...,
        min_length=16,
        description="Invitation token received by the salesperson.",
    )

