"""Response schemas for authentication-related API operations."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from core.models.user_model import UserRole


class UserProfileResponse(BaseModel):
    """Public user profile data returned in authentication responses."""

    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: str = Field(..., description="User identifier.")
    first_name: str = Field(..., description="First name of the user.")
    last_name: str = Field(..., description="Last name of the user.")
    email: EmailStr = Field(..., description="Email address of the user.")
    phone_number: str | None = Field(
        default=None,
        description="Phone number of the user, when available.",
    )
    role: UserRole = Field(..., description="Role assigned to the user.")
    is_active: bool = Field(..., description="Whether the user account is active.")


class OtpSentResponse(BaseModel):
    """Response payload after an OTP has been generated and sent."""

    model_config = ConfigDict(extra="forbid")

    message: str = Field(..., description="Human-readable OTP dispatch result.")
    delivery_channel: str = Field(
        default="email",
        description="Delivery channel used for the OTP handoff.",
    )
    dev_otp: str | None = Field(
        default=None,
        description="Development-only OTP preview returned outside production.",
    )


class LoginResponse(BaseModel):
    """Response payload after a successful authentication flow."""

    model_config = ConfigDict(extra="forbid")

    access_token: str = Field(..., description="JWT access token for the session.")
    token_type: str = Field(default="bearer", description="Authentication token type.")
    user: UserProfileResponse = Field(..., description="Authenticated user profile.")
    last_login_at: datetime | None = Field(
        default=None,
        description="UTC timestamp of the most recent successful login.",
    )

