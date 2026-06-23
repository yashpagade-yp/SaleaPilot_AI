"""Controller logic for conversation-related workflows."""

from datetime import datetime, timezone

from fastapi import HTTPException, status

from commons.logger import logger
from core.cruds.conversation_crud import CRUDConversation
from core.cruds.training_session_crud import CRUDTrainingSession
from core.database.database import get_utc_now
from core.models.conversation_model import Conversation
from core.models.training_session_model import TrainingSessionStatus
from core.services.eigi_service import EigiService

logging = logger(__name__)


class ConversationController:
    """Business orchestration for conversation history workflows."""

    def __init__(self) -> None:
        """Initialize CRUD dependencies for conversation workflows."""
        self.crud_conversation = CRUDConversation()
        self.crud_training_session = CRUDTrainingSession()
        self.eigi_service = EigiService()

    @staticmethod
    def _as_utc(value: datetime | None) -> datetime | None:
        """Normalize a datetime value to UTC-aware form.

        Args:
            value (datetime | None): Datetime value loaded from persistence.

        Returns:
            datetime | None: UTC-aware datetime or None when no value exists.
        """
        if value is None:
            return None
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    @staticmethod
    def _serialize_conversation(conversation: Conversation) -> dict:
        """Convert a conversation model into the response shape.

        Args:
            conversation (Conversation): Persisted conversation model.

        Returns:
            dict: Conversation response payload.
        """
        return {
            "id": str(conversation.id),
            "training_session_id": conversation.training_session_id,
            "conversation_id": conversation.conversation_id,
            "agent_id": conversation.agent_id,
            "conversation_type": conversation.conversation_type,
            "conversation_status": conversation.conversation_status,
            "conversation_visibility": conversation.conversation_visibility,
            "transcript": conversation.transcript,
            "analysis": conversation.analysis,
            "fetched_at": conversation.fetched_at,
        }

    async def get_conversation_detail(self, *, training_session_id: str) -> dict:
        """Fetch one conversation record by training session identifier.

        Args:
            training_session_id (str): Training session identifier.

        Returns:
            dict: Serialized conversation response payload.

        Raises:
            HTTPException: If the conversation record is not found.
        """
        try:
            logging.info("Executing ConversationController.get_conversation_detail")
            conversation = await self.crud_conversation.get_by_training_session_id(
                training_session_id=training_session_id
            )
            if conversation is None:
                logging.warning(
                    f"No conversation found for training session {training_session_id}"
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found",
                )

            return self._serialize_conversation(conversation)
        except HTTPException:
            raise
        except Exception as error:
            logging.error(f"Error in ConversationController.get_conversation_detail: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )

    async def list_conversation_history(
        self,
        *,
        training_session_ids: list[str],
        page: int,
        page_size: int,
    ) -> dict:
        """List conversation history for known training session identifiers.

        Args:
            training_session_ids (list[str]): Session identifiers belonging to a user.
            page (int): Page number.
            page_size (int): Maximum items per page.

        Returns:
            dict: Paginated conversation list response payload.
        """
        try:
            logging.info("Executing ConversationController.list_conversation_history")
            items: list[dict] = []
            for training_session_id in training_session_ids:
                conversation = await self.crud_conversation.get_by_training_session_id(
                    training_session_id=training_session_id
                )
                if conversation is not None:
                    items.append(self._serialize_conversation(conversation))

            total = len(items)
            start_index = (page - 1) * page_size
            end_index = start_index + page_size

            return {
                "items": items[start_index:end_index],
                "page": page,
                "page_size": page_size,
                "total": total,
            }
        except Exception as error:
            logging.error(f"Error in ConversationController.list_conversation_history: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )

    async def sync_conversation(self, *, training_session_id: str) -> dict:
        """Sync one conversation record from Eigi into local persistence.

        Args:
            training_session_id (str): Training session identifier.

        Returns:
            dict: Serialized synced conversation payload.

        Raises:
            HTTPException: If the session or conversation mapping does not exist.
        """
        try:
            logging.info("Executing ConversationController.sync_conversation")
            training_session = await self.crud_training_session.get_by_id(
                id=training_session_id
            )
            if training_session is None:
                logging.warning(
                    f"No training session found for sync: {training_session_id}"
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Training session not found",
                )

            if not training_session.conversation_id:
                logging.warning(
                    f"Training session has no Eigi conversation id: {training_session_id}"
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Training session is not linked to an Eigi conversation yet",
                )

            conversation = await self.crud_conversation.get_by_training_session_id(
                training_session_id=training_session_id
            )
            if conversation is None:
                logging.warning(
                    f"No local conversation found for sync: {training_session_id}"
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found",
                )

            eigi_payload = await self.eigi_service.get_conversation_detail(
                conversation_id=training_session.conversation_id
            )
            synced_status = eigi_payload.get(
                "conversation_status", conversation.conversation_status
            )
            transcript_payload = eigi_payload.get("conversation_transcript")
            transcript_text = None
            if transcript_payload is not None:
                from core.services.feedback_service import FeedbackGenerationService

                transcript_text = FeedbackGenerationService().normalize_transcript(
                    transcript_payload
                )

            conversation = await self.crud_conversation.update(
                id=str(conversation.id),
                obj_in={
                    "conversation_status": synced_status,
                    "transcript": transcript_text,
                    "analysis": eigi_payload.get("conversation_analysis") or {},
                    "raw_payload": eigi_payload,
                    "fetched_at": get_utc_now(),
                },
            )
            if conversation is None:
                logging.error(
                    f"Failed to update local conversation during sync: {training_session_id}"
                )
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to update conversation during sync",
                )

            session_update: dict = {}
            if synced_status == "COMPLETED":
                session_update["status"] = TrainingSessionStatus.COMPLETED
                session_update["ended_at"] = get_utc_now()
                started_at = self._as_utc(training_session.started_at)
                if started_at is not None:
                    session_update["duration_seconds"] = int(
                        (get_utc_now() - started_at).total_seconds()
                    )
            elif synced_status == "FAILED":
                session_update["status"] = TrainingSessionStatus.FAILED
            elif synced_status == "CANCELLED":
                session_update["status"] = TrainingSessionStatus.CANCELLED

            if session_update:
                await self.crud_training_session.update(
                    id=str(training_session.id),
                    obj_in=session_update,
                )

            return self._serialize_conversation(conversation)
        except HTTPException:
            raise
        except Exception as error:
            logging.error(f"Error in ConversationController.sync_conversation: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )
