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


class AdminVerifyOtpRequest(BaseModel):
    """Request payload for verifying an admin login OTP."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    phone_number: str = Field(
        ...,
        min_length=10,
        max_length=20,
        description="Admin phone number associated with the OTP.",
    )
    otp: str = Field(
        ...,
        min_length=4,
        max_length=8,
        description="OTP code entered by the admin.",
    )


class SalespersonLoginRequest(BaseModel):
    """Request payload for salesperson login."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    email: EmailStr = Field(
        ...,
        description="Salesperson email used for login.",
    )
    password: str = Field(
        ...,
        min_length=8,
        description="Salesperson plain-text password submitted for verification.",
    )


class ResetPasswordRequest(BaseModel):
    """Request payload for initiating a password reset."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    email: EmailStr = Field(
        ...,
        description="Email address of the user requesting password reset.",
    )

