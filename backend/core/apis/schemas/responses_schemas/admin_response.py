"""Response schemas for admin management API operations."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from core.models.user_model import UserRole


class AdminSalespersonResponse(BaseModel):
    """Response payload for one salesperson row in the admin dashboard."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., description="Salesperson user identifier.")
    first_name: str = Field(..., description="Salesperson first name.")
    last_name: str = Field(..., description="Salesperson last name.")
    email: EmailStr = Field(..., description="Salesperson email address.")
    phone_number: str | None = Field(
        default=None,
        description="Salesperson phone number or placeholder value when present.",
    )
    role: UserRole = Field(..., description="Platform role assigned to the user.")
    is_active: bool = Field(..., description="Whether the salesperson can currently sign in.")
    status: str = Field(
        ...,
        description="Dashboard status such as INVITED, ACTIVE, or INACTIVE.",
    )
    last_login_at: datetime | None = Field(
        default=None,
        description="UTC timestamp of the salesperson's latest successful login.",
    )
    updated_at: datetime = Field(..., description="UTC timestamp when the user record was last updated.")
    latest_invitation_sent_at: datetime | None = Field(
        default=None,
        description="UTC timestamp when the latest invitation was created.",
    )
    latest_invitation_expires_at: datetime | None = Field(
        default=None,
        description="UTC timestamp when the latest invitation expires.",
    )
    latest_invitation_status: str | None = Field(
        default=None,
        description="Latest invitation lifecycle state when one exists.",
    )


class AdminSalespersonListResponse(BaseModel):
    """Response payload for listing salespeople in the admin dashboard."""

    model_config = ConfigDict(extra="forbid")

    items: list[AdminSalespersonResponse] = Field(
        ...,
        description="Salesperson records available to the admin dashboard.",
    )


class AdminActionResponse(BaseModel):
    """Response payload for admin actions that return a simple message."""

    model_config = ConfigDict(extra="forbid")

    message: str = Field(..., description="Human-readable admin action result.")
