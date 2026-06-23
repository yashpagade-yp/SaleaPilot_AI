"""Service layer for Eigi API integrations used by SalesPilot."""

from typing import Any

import httpx
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from commons.logger import logger

load_dotenv()

logging = logger(__name__)


class EigiSettings(BaseSettings):
    """Environment-backed Eigi API settings."""

    eigi_api_key: str = Field(..., alias="EIGI_API_KEY")
    eigi_base_url: str = Field(..., alias="EIGI_BASE_URL")
    eigi_daily_endpoint: str = Field(..., alias="EIGI_DAILY_ENDPOINT")

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        populate_by_name=True,
    )


class EigiService:
    """Service facade for Eigi Daily and conversation APIs."""

    def __init__(self) -> None:
        """Initialize Eigi service configuration and HTTP defaults."""
        logging.info("Executing EigiService.__init__")
        self.settings = EigiSettings()
        self.timeout = httpx.Timeout(30.0, connect=10.0)

    @property
    def headers(self) -> dict[str, str]:
        """Build standard headers for authenticated Eigi API calls.

        Returns:
            dict[str, str]: Header mapping with API key and JSON content type.
        """
        return {
            "X-API-Key": self.settings.eigi_api_key,
            "Content-Type": "application/json",
        }

    def build_daily_url(self) -> str:
        """Build the absolute Eigi Daily session creation URL.

        Returns:
            str: Absolute URL for the configured Eigi Daily endpoint.
        """
        return (
            f"{self.settings.eigi_base_url.rstrip('/')}"
            f"/{self.settings.eigi_daily_endpoint.lstrip('/')}"
        )

    def build_conversation_detail_url(self, *, conversation_id: str) -> str:
        """Build the absolute URL for one Eigi conversation detail request.

        Args:
            conversation_id (str): Eigi conversation identifier.

        Returns:
            str: Absolute URL for one conversation detail request.
        """
        return (
            f"{self.settings.eigi_base_url.rstrip('/')}"
            f"/v1/public/conversations/{conversation_id}"
        )

    async def create_daily_session(
        self,
        *,
        agent_id: str,
        conversation_metadata: dict[str, Any],
        conversation_visibility: bool = False,
        conversation_config_type: str = "VOICE",
    ) -> dict[str, Any]:
        """Create a Daily-backed voice session through Eigi.

        Args:
            agent_id (str): Eigi agent identifier for the selected persona.
            conversation_metadata (dict[str, Any]): Session metadata payload.
            conversation_visibility (bool): Eigi visibility flag for the conversation.
            conversation_config_type (str): Conversation runtime type.

        Returns:
            dict[str, Any]: Parsed Eigi API response payload.

        Raises:
            httpx.HTTPStatusError: If Eigi returns a non-success status code.
            Exception: If the HTTP request fails unexpectedly.
        """
        try:
            logging.info("Executing EigiService.create_daily_session")
            payload = {
                "agent_id": agent_id,
                "conversation_metadata": conversation_metadata,
                "conversation_visibility": conversation_visibility,
                "conversation_config_type": conversation_config_type,
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.build_daily_url(),
                    headers=self.headers,
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()

            logging.info(
                "Eigi Daily session created successfully for agent "
                f"{agent_id} with conversation id {data.get('conversation_id')}"
            )
            return data
        except Exception as error:
            logging.error(f"Error in EigiService.create_daily_session: {error}")
            raise error

    async def get_conversation_detail(self, *, conversation_id: str) -> dict[str, Any]:
        """Fetch one conversation payload from Eigi by conversation identifier.

        Args:
            conversation_id (str): Eigi conversation identifier.

        Returns:
            dict[str, Any]: Parsed Eigi conversation payload.

        Raises:
            httpx.HTTPStatusError: If Eigi returns a non-success status code.
            Exception: If the HTTP request fails unexpectedly.
        """
        try:
            logging.info("Executing EigiService.get_conversation_detail")
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    self.build_conversation_detail_url(conversation_id=conversation_id),
                    headers={"X-API-Key": self.settings.eigi_api_key},
                )
                response.raise_for_status()
                data = response.json()

            logging.info(
                "Fetched Eigi conversation payload successfully for conversation id "
                f"{conversation_id}"
            )
            return data
        except Exception as error:
            logging.error(f"Error in EigiService.get_conversation_detail: {error}")
            raise error
