"""Request schemas for feedback-related API operations."""

from pydantic import BaseModel, ConfigDict, Field


class FeedbackDetailRequest(BaseModel):
    """Request schema for fetching one feedback record by session reference."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    training_session_id: str = Field(
        ...,
        description="Training session identifier whose feedback should be fetched.",
    )

