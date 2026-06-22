"""Invitation model definitions for salesperson onboarding."""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from odmantic import Field, Model
from odmantic.config import ODMConfigDict
from pydantic import EmailStr

from core.models.user_model import UserRole


def utc_now() -> datetime:
    """Return the current UTC datetime.

    This helper keeps timestamp defaults consistent across invitation records.

    Returns:
        datetime: Current UTC-aware datetime.
    """
    return datetime.now(timezone.utc)


class InvitationStatus(str, Enum):
    """Allowed states for salesperson invitation records."""

    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"


class Invitation(Model):
    """Persisted invitation record for salesperson onboarding.

    Stores the invitation lifecycle separately from the user account so the
    platform can track pending, accepted, expired, or cancelled invites.
    """

    email: EmailStr = Field(
        ...,
        description="Email address receiving the invitation.",
    )
    role: UserRole = Field(
        default=UserRole.SALESPERSON,
        description="Role granted when the invitation is accepted.",
    )
    invited_by: str = Field(
        ...,
        description="User identifier of the admin who sent the invitation.",
    )
    status: InvitationStatus = Field(
        default=InvitationStatus.PENDING,
        description="Current state of the invitation lifecycle.",
    )
    token: str = Field(
        ...,
        min_length=16,
        unique=True,
        description="Unique token used to identify and accept the invitation.",
    )
    expires_at: datetime = Field(
        ...,
        description="UTC timestamp when the invitation becomes invalid.",
    )
    accepted_at: Optional[datetime] = Field(
        default=None,
        description="UTC timestamp when the invite was accepted.",
    )
    created_at: datetime = Field(
        default_factory=utc_now,
        description="UTC timestamp when the record was created.",
    )
    updated_at: datetime = Field(
        default_factory=utc_now,
        description="UTC timestamp when the record was last updated.",
    )

    model_config = ODMConfigDict(
        collection="invitations",
        extra="forbid",
    )
