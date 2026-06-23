"""Controller logic for training session workflows."""

import httpx

from fastapi import HTTPException, status

from commons.logger import logger
from core.cruds.conversation_crud import CRUDConversation
from core.cruds.scenario_crud import CRUDScenario
from core.cruds.training_session_crud import CRUDTrainingSession
from core.cruds.user_crud import CRUDUser
from core.database.database import get_utc_now
from core.models.conversation_model import ConversationStatus
from core.models.training_session_model import TrainingSessionStatus
from core.models.training_session_model import TrainingSession
from core.services.eigi_service import EigiService

logging = logger(__name__)


class TrainingSessionController:
    """Business orchestration for training session workflows."""

    def __init__(self) -> None:
        """Initialize CRUD dependencies for training-session workflows."""
        self.crud_user = CRUDUser()
        self.crud_scenario = CRUDScenario()
        self.crud_training_session = CRUDTrainingSession()
        self.crud_conversation = CRUDConversation()
        self.eigi_service = EigiService()

    @staticmethod
    def _serialize_training_session(training_session: TrainingSession) -> dict:
        """Convert a training session model into the response shape.

        Args:
            training_session (TrainingSession): Persisted training session model.

        Returns:
            dict: Training session response payload.
        """
        return {
            "id": str(training_session.id),
            "user_id": training_session.user_id,
            "scenario_id": training_session.scenario_id,
            "scenario_key": training_session.scenario_key,
            "agent_id": training_session.agent_id,
            "status": training_session.status,
            "conversation_id": training_session.conversation_id,
            "started_at": training_session.started_at,
            "ended_at": training_session.ended_at,
        }

    async def start_training_session(self, *, user_id: str, scenario_key) -> dict:
        """Create a training session record for a salesperson.

        Args:
            user_id (str): Salesperson user identifier.
            scenario_key: Fixed scenario key requested for the session.

        Returns:
            dict: Training session creation response payload.

        Raises:
            HTTPException: If the user or scenario is invalid for session creation.
        """
        try:
            logging.info("Executing TrainingSessionController.start_training_session")
            user = await self.crud_user.get_by_id(id=user_id)
            if user is None:
                logging.warning(f"Training session requested for unknown user {user_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )

            scenario = await self.crud_scenario.get_by_key(key=scenario_key)
            if scenario is None or not scenario.is_active:
                logging.warning(f"Training session requested for unavailable scenario {scenario_key}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Scenario not found or inactive",
                )

            conversation_name = f"{user.first_name} {user.last_name}".strip()
            training_session = await self.crud_training_session.create(
                obj_in={
                    "user_id": str(user.id),
                    "scenario_id": str(scenario.id),
                    "scenario_key": scenario.key,
                    "agent_id": scenario.agent_id,
                    "conversation_name": conversation_name,
                    "conversation_metadata": {
                        "user_id": str(user.id),
                        "user_name": conversation_name,
                        "scenario": scenario.key,
                        "name": conversation_name,
                        "agent_id": scenario.agent_id,
                    },
                }
            )

            conversation_metadata = dict(training_session.conversation_metadata)
            conversation_metadata["session_id"] = str(training_session.id)
            conversation_metadata["scenario"] = str(scenario.key)
            conversation_metadata["name"] = conversation_name
            conversation_metadata["agent_id"] = scenario.agent_id

            eigi_response = await self.eigi_service.create_daily_session(
                agent_id=scenario.agent_id,
                conversation_metadata=conversation_metadata,
            )

            training_session = await self.crud_training_session.update(
                id=str(training_session.id),
                obj_in={
                    "conversation_metadata": conversation_metadata,
                    "eigi_record_id": eigi_response.get("id"),
                    "conversation_id": eigi_response.get("conversation_id"),
                    "daily_room": eigi_response.get("dailyRoom"),
                    "daily_token": eigi_response.get("dailyToken"),
                    "status": TrainingSessionStatus.IN_PROGRESS,
                    "started_at": get_utc_now(),
                },
            )
            if training_session is None:
                logging.error("Training session disappeared during Eigi session creation")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to update training session after Eigi session creation",
                )

            await self.crud_conversation.create(
                obj_in={
                    "training_session_id": str(training_session.id),
                    "conversation_id": training_session.conversation_id,
                    "agent_id": training_session.agent_id,
                    "conversation_status": ConversationStatus.IN_PROGRESS,
                    "conversation_visibility": False,
                    "raw_payload": eigi_response,
                    "fetched_at": get_utc_now(),
                }
            )

            return {
                "session_id": str(training_session.id),
                "eigi_record_id": training_session.eigi_record_id,
                "conversation_id": training_session.conversation_id,
                "daily_room": training_session.daily_room,
                "daily_token": training_session.daily_token,
                "status": training_session.status,
            }
        except HTTPException:
            raise
        except httpx.HTTPStatusError as error:
            if "training_session" in locals():
                await self.crud_training_session.update(
                    id=str(training_session.id),
                    obj_in={"status": TrainingSessionStatus.FAILED},
                )
            logging.error(
                "Error in TrainingSessionController.start_training_session while calling "
                f"Eigi: {error.response.text}"
            )
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Failed to create Eigi Daily session",
            )
        except Exception as error:
            if "training_session" in locals():
                await self.crud_training_session.update(
                    id=str(training_session.id),
                    obj_in={"status": TrainingSessionStatus.FAILED},
                )
            logging.error(f"Error in TrainingSessionController.start_training_session: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )

    async def list_user_training_sessions(self, *, user_id: str) -> list[dict]:
        """List all training sessions created by one salesperson.

        Args:
            user_id (str): Salesperson user identifier.

        Returns:
            list[dict]: Serialized training session records.

        Raises:
            HTTPException: If the user does not exist or the lookup fails.
        """
        try:
            logging.info("Executing TrainingSessionController.list_user_training_sessions")
            user = await self.crud_user.get_by_id(id=user_id)
            if user is None:
                logging.warning(f"Training session list requested for unknown user {user_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )

            sessions = await self.crud_training_session.list_by_user_id(user_id=str(user.id))
            return [self._serialize_training_session(session) for session in sessions]
        except HTTPException:
            raise
        except Exception as error:
            logging.error(f"Error in TrainingSessionController.list_user_training_sessions: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )
