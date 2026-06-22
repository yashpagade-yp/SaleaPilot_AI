"""Request schemas for conversation-related API operations."""

from pydantic import BaseModel, ConfigDict, Field


class ConversationHistoryRequest(BaseModel):
    """Request schema for listing conversation history for a user."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    page: int = Field(
        default=1,
        ge=1,
        description="Page number for paginated conversation history.",
    )
    page_size: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum number of records returned in one page.",
    )


class ConversationDetailRequest(BaseModel):
    """Request schema for fetching a single conversation by session reference."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    training_session_id: str = Field(
        ...,
        description="Training session identifier whose conversation should be fetched.",
    )

