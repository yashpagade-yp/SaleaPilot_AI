"""Request schemas for authentication-related API operations."""

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class AdminLoginRequest(BaseModel):
    """Request payload for admin login with phone number and password."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    phone_number: str = Field(
        ...,
        min_length=10,
        max_length=20,
        description="Admin phone number used for login.",
    )
    password: str = Field(
        ...,
        min_length=8,
        description="Admin plain-text password submitted for verification.",
    )

class SalespersonOtpRequest(BaseModel):
    """Request payload for starting salesperson email-OTP login."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    email: EmailStr = Field(
        ...,
        description="Invited salesperson email used for OTP delivery.",
    )


class SalespersonVerifyOtpRequest(BaseModel):
    """Request payload for verifying salesperson email OTP."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    email: EmailStr = Field(
        ...,
        description="Invited salesperson email associated with the OTP.",
    )
    otp: str = Field(
        ...,
        min_length=4,
        max_length=8,
        description="OTP code entered by the salesperson.",
    )


class ResetPasswordRequest(BaseModel):
    """Request payload for initiating a password reset."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    email: EmailStr = Field(
        ...,
        description="Email address of the user requesting password reset.",
    )

