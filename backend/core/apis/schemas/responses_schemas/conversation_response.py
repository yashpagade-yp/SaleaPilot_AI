"""Response schemas for conversation-related API operations."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from core.models.conversation_model import ConversationStatus, ConversationType


class ConversationResponse(BaseModel):
    """Response payload for one synced conversation record."""

    model_config = ConfigDict(from_attributes=True, extra="forbid")

    id: str = Field(..., description="Conversation record identifier.")
    training_session_id: str = Field(..., description="Owning training session identifier.")
    conversation_id: str = Field(..., description="Eigi conversation identifier.")
    agent_id: str = Field(..., description="Eigi agent identifier used in the call.")
    conversation_type: ConversationType = Field(..., description="Type of conversation.")
    conversation_status: ConversationStatus = Field(..., description="Conversation status.")
    conversation_visibility: bool = Field(..., description="Conversation visibility flag.")
    transcript: str | None = Field(
        default=None,
        description="Conversation transcript, when available.",
    )
    analysis: dict[str, Any] = Field(
        default_factory=dict,
        description="Structured Eigi analysis payload, when available.",
    )
    fetched_at: datetime | None = Field(
        default=None,
        description="UTC timestamp when the latest conversation payload was fetched.",
    )


class ConversationListResponse(BaseModel):
    """Response payload for listing conversation history."""

    model_config = ConfigDict(extra="forbid")

    items: list[ConversationResponse] = Field(..., description="Conversation history entries.")
    page: int = Field(..., description="Current page number.")
    page_size: int = Field(..., description="Number of items returned in the page.")
    total: int = Field(..., description="Total matching records.")

