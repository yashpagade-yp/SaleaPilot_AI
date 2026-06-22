"""Scenario model definitions for fixed training personas."""

from datetime import datetime, timezone
from enum import Enum

from odmantic import Field, Model
from odmantic.config import ODMConfigDict

def utc_now() -> datetime:
    """Return the current UTC datetime.

    This helper keeps timestamp defaults consistent across scenario records.

    Returns:
        datetime: Current UTC-aware datetime.
    """
    return datetime.now(timezone.utc)


class ScenarioKey(str, Enum):
    """Fixed scenario keys supported by the MVP."""

    IDEAL = "IDEAL"
    RUDE = "RUDE"
    CONFUSED = "CONFUSED"
    BUSY = "BUSY"


class Scenario(Model):
    """Persisted training persona definition for the platform.

    Each scenario maps a fixed persona key to one Eigi agent identifier used
    during Daily-based voice training sessions.
    """

    key: ScenarioKey = Field(
        ...,
        description="Fixed scenario key used by the product.",
    )
    title: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Human-readable scenario title.",
    )
    description: str = Field(
        ...,
        min_length=5,
        max_length=500,
        description="Short explanation of the persona behavior.",
    )
    agent_id: str = Field(
        ...,
        min_length=8,
        description="Eigi agent identifier mapped to this scenario.",
    )
    is_active: bool = Field(
        default=True,
        description="Whether the scenario is currently available for selection.",
    )
    sort_order: int = Field(
        default=0,
        ge=0,
        description="Display order used in scenario listing screens.",
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
        collection="scenarios",
        extra="forbid",
    )
