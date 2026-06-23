"""Controller logic for conversation-related workflows."""

from fastapi import HTTPException, status

from commons.logger import logger
from core.cruds.conversation_crud import CRUDConversation
from core.models.conversation_model import Conversation

logging = logger(__name__)


class ConversationController:
    """Business orchestration for conversation history workflows."""

    def __init__(self) -> None:
        """Initialize CRUD dependencies for conversation workflows."""
        self.crud_conversation = CRUDConversation()

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
