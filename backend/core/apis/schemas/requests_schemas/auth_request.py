"""Request schemas for authentication-related API operations."""

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class AdminLoginRequest(BaseModel):
    """Request payload for admin login with email and password."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    email: EmailStr = Field(
        ...,
        description="Admin email address used for login.",
    )
    password: str = Field(
        ...,
        min_length=8,
        description="Admin plain-text password submitted for verification.",
    )


class LoginRequest(BaseModel):
    """Request payload for unified user login with email and password."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    email: EmailStr = Field(
        ...,
        description="User email address used for login.",
    )
    password: str = Field(
        ...,
        min_length=8,
        description="User plain-text password submitted for verification.",
    )


class AdminVerifyOtpRequest(BaseModel):
    """Request payload for verifying admin email OTP."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    email: EmailStr = Field(
        ...,
        description="Admin email address associated with the OTP.",
    )
    otp: str = Field(
        ...,
        min_length=4,
        max_length=8,
        description="OTP code entered by the admin.",
    )


class VerifyOtpRequest(BaseModel):
    """Request payload for unified OTP verification."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    email: EmailStr = Field(
        ...,
        description="User email address associated with the OTP.",
    )
    otp: str = Field(
        ...,
        min_length=4,
        max_length=8,
        description="OTP code entered by the user.",
    )


class SalespersonOtpRequest(BaseModel):
    """Request payload for starting invitation-based salesperson onboarding OTP."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    invitation_token: str = Field(
        ...,
        min_length=16,
        description="Invitation token copied from the salesperson invitation email.",
    )
    email: EmailStr = Field(
        ...,
        description="Invited salesperson email used for OTP delivery.",
    )


class SalespersonLoginRequest(BaseModel):
    """Request payload for returning salesperson login with email and password."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    email: EmailStr = Field(
        ...,
        description="Salesperson email address used for login.",
    )
    password: str = Field(
        ...,
        min_length=8,
        description="Salesperson plain-text password submitted for verification.",
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


class SalespersonCompleteProfileRequest(BaseModel):
    """Request payload for completing salesperson onboarding after invitation acceptance."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    invitation_token: str = Field(
        ...,
        min_length=16,
        description="Invitation token copied from the invitation email.",
    )
    email: EmailStr = Field(
        ...,
        description="Invited salesperson email address used for OTP delivery.",
    )
    first_name: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="First name entered by the invited salesperson.",
    )
    last_name: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Last name entered by the invited salesperson.",
    )
    otp: str = Field(
        ...,
        min_length=4,
        max_length=8,
        description="OTP code received by email.",
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Password created by the invited salesperson.",
    )


class ResetPasswordRequest(BaseModel):
    """Request payload for initiating a password reset."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    email: EmailStr = Field(
        ...,
        description="Email address of the user requesting password reset.",
    )

