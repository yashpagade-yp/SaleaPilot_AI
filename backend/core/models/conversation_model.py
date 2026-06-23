"""Conversation model definitions for Eigi-synced call records."""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional

from odmantic import Field, Model
from odmantic.config import ODMConfigDict

def utc_now() -> datetime:
    """Return the current UTC datetime.

    This helper keeps timestamp defaults consistent across conversation records.

    Returns:
        datetime: Current UTC-aware datetime.
    """
    return datetime.now(timezone.utc)


class ConversationStatus(str, Enum):
    """Lifecycle states for a synced conversation record."""

    CREATED = "CREATED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class ConversationType(str, Enum):
    """Supported conversation types for the current product scope."""

    DAILY = "DAILY"
    TELEPHONY = "TELEPHONY"
    WHATSAPP = "WHATSAPP"
    CHAT = "CHAT"


class Conversation(Model):
    """Persisted conversation record associated with one training session.

    Stores the data fetched or synced from Eigi after or during a Daily voice
    conversation so history and transcript views can be built reliably.
    """

    training_session_id: str = Field(
        ...,
        unique=True,
        description="Training session identifier owning this conversation.",
    )
    conversation_id: str = Field(
        ...,
        description="Eigi conversation identifier for this synced record.",
    )
    agent_id: str = Field(
        ...,
        min_length=8,
        description="Eigi agent identifier used during the conversation.",
    )
    conversation_type: ConversationType = Field(
        default=ConversationType.DAILY,
        description="Type of conversation represented by this record.",
    )
    conversation_status: ConversationStatus = Field(
        default=ConversationStatus.CREATED,
        description="Current lifecycle state of the conversation.",
    )
    conversation_visibility: bool = Field(
        default=False,
        description="Visibility flag used when the conversation was created.",
    )
    transcript: Optional[str] = Field(
        default=None,
        description="Conversation transcript text or normalized transcript payload.",
    )
    analysis: Dict[str, Any] = Field(
        default_factory=dict,
        description="Structured analysis data returned by Eigi, if available.",
    )
    raw_payload: Dict[str, Any] = Field(
        default_factory=dict,
        description="Raw Eigi conversation payload stored for traceability.",
    )
    fetched_at: Optional[datetime] = Field(
        default=None,
        description="UTC timestamp when the latest Eigi payload was fetched.",
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
        collection="conversations",
        extra="forbid",
    )
