"""User model definitions for admin and salesperson accounts."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional

from odmantic import Field as ODMField, Model
from odmantic.config import ODMConfigDict
from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field as PydanticField,
    model_validator,
)

def utc_now() -> datetime:
    """Return the current UTC datetime.

    This helper keeps timestamp defaults consistent across user-related models.

    Returns:
        datetime: Current UTC-aware datetime.
    """
    return datetime.now(timezone.utc)


class UserRole(str, Enum):
    """Allowed platform roles for user accounts."""

    ADMIN = "ADMIN"
    SALESPERSON = "SALESPERSON"


class OtpPurpose(str, Enum):
    """Supported OTP purposes for authentication flows."""

    ADMIN_LOGIN = "ADMIN_LOGIN"
    SALESPERSON_LOGIN = "SALESPERSON_LOGIN"
    PASSWORD_RESET = "PASSWORD_RESET"
    INVITATION_VERIFICATION = "INVITATION_VERIFICATION"


class Address(BaseModel):
    """Embedded postal address details for a user."""

    model_config = ConfigDict(
        validate_assignment=True,
        use_enum_values=True,
        str_strip_whitespace=True,
        extra="forbid",
    )

    street: Optional[str] = PydanticField(
        default=None,
        max_length=200,
        description="Street address line.",
    )
    city: Optional[str] = PydanticField(
        default=None,
        max_length=100,
        description="City name.",
    )
    state: Optional[str] = PydanticField(
        default=None,
        max_length=100,
        description="State or province name.",
    )
    postal_code: Optional[str] = PydanticField(
        default=None,
        max_length=20,
        description="Postal or ZIP code.",
    )
    country: Optional[str] = PydanticField(
        default=None,
        max_length=100,
        description="Country name.",
    )


class UserOtp(BaseModel):
    """Embedded active OTP state stored with the user record."""

    model_config = ConfigDict(
        validate_assignment=True,
        use_enum_values=True,
        str_strip_whitespace=True,
        extra="forbid",
    )

    code_hash: str = PydanticField(
        ...,
        min_length=20,
        description="Hashed OTP value. Plain OTP values must never be stored.",
    )
    purpose: OtpPurpose = PydanticField(
        ...,
        description="Business purpose for the currently active OTP.",
    )
    expires_at: datetime = PydanticField(
        ...,
        description="UTC timestamp when the OTP expires.",
    )
    requested_at: datetime = PydanticField(
        default_factory=utc_now,
        description="UTC timestamp when the OTP was requested.",
    )
    attempt_count: int = PydanticField(
        default=0,
        ge=0,
        le=5,
        description="Failed verification attempts for the active OTP.",
    )
    attempt_window_started_at: datetime = PydanticField(
        default_factory=utc_now,
        description="UTC timestamp when the current OTP attempt window started.",
    )


class User(Model):
    """Persisted user record for admin and salesperson accounts.

    Stores the shared identity and authentication fields needed by both user
    roles. Role-specific behavior, such as admin invitation privileges or
    salesperson training access, should be enforced by controllers/services.
    """

    first_name: str = ODMField(
        ...,
        min_length=2,
        max_length=50,
        description="First name of the user.",
    )
    last_name: str = ODMField(
        ...,
        min_length=2,
        max_length=50,
        description="Last name of the user.",
    )
    email: EmailStr = ODMField(
        ...,
        unique=True,
        description="Primary email address for account communication.",
    )
    phone_number: Optional[str] = ODMField(
        default=None,
        min_length=10,
        max_length=20,
        unique=True,
        description="Phone number used for admin login and OTP flows.",
    )
    password_hash: str = ODMField(
        ...,
        min_length=20,
        description="Hashed password value. Plain text passwords must never be stored.",
    )
    role: UserRole = ODMField(
        ...,
        description="Platform role of the user.",
    )
    address: Optional[Address] = ODMField(
        default=None,
        description="Optional embedded postal address for the user.",
    )
    otp: Optional[UserOtp] = ODMField(
        default=None,
        description="Optional active OTP state for authentication flows.",
    )
    auth_metadata: Dict[str, Any] = ODMField(
        default_factory=dict,
        description="Extensible auth-related metadata for the user account.",
    )
    is_active: bool = ODMField(
        default=True,
        description="Whether the account is active and allowed to use the platform.",
    )
    last_login_at: Optional[datetime] = ODMField(
        default=None,
        description="UTC timestamp of the latest successful login.",
    )
    created_at: datetime = ODMField(
        default_factory=utc_now,
        description="UTC timestamp when the record was created.",
    )
    updated_at: datetime = ODMField(
        default_factory=utc_now,
        description="UTC timestamp when the record was last updated.",
    )

    model_config = ODMConfigDict(
        collection="users",
        extra="forbid",
    )

    @model_validator(mode="after")
    def validate_role_auth_requirements(self) -> "User":
        """Validate role-specific authentication requirements.

        Ensures admin users always have the required login fields and that
        salesperson accounts keep a valid email identity for invitation and
        login-related flows.

        Returns:
            User: The validated user instance.

        Raises:
            ValueError: If role-specific required fields are missing.
        """
        if self.role == UserRole.ADMIN:
            if not self.password_hash:
                raise ValueError("Admin users must have a password_hash.")

        if self.role == UserRole.SALESPERSON and not self.email:
            raise ValueError("Salesperson users must have an email.")

        return self
