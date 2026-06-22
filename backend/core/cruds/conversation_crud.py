"""CRUD operations for conversation records."""

from fastapi import HTTPException, status

from commons.logger import logger
from core.database.database import get_engine, get_utc_now, parse_object_id
from core.models.conversation_model import Conversation

logging = logger(__name__)


class CRUDConversation:
    """Database access layer for conversation records."""

    async def create(self, *, obj_in: dict) -> Conversation:
        """Create a new conversation record.

        Args:
            obj_in (dict): Conversation creation payload.

        Returns:
            Conversation: Created conversation model instance.

        Raises:
            Exception: If the database write fails.
        """
        try:
            logging.info("Executing CRUDConversation.create")
            conversation = Conversation(**obj_in)
            await get_engine().save(conversation)
            return conversation
        except Exception as error:
            logging.error(f"Error in CRUDConversation.create: {error}")
            raise error

    async def get_by_id(self, *, id: str) -> Conversation | None:
        """Read a conversation record by unique identifier.

        Args:
            id (str): Conversation identifier.

        Returns:
            Conversation | None: Matching conversation model or None.

        Raises:
            HTTPException 400: If the identifier is invalid.
            Exception: If the database read fails.
        """
        try:
            logging.info("Executing CRUDConversation.get_by_id")
            return await get_engine().find_one(
                Conversation,
                Conversation.id == parse_object_id(id),
            )
        except ValueError as error:
            logging.warning(f"Invalid conversation id received: {id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(error),
            ) from error
        except Exception as error:
            logging.error(f"Error in CRUDConversation.get_by_id: {error}")
            raise error

    async def get_by_training_session_id(
        self,
        *,
        training_session_id: str,
    ) -> Conversation | None:
        """Read a conversation record by owning training session identifier.

        Args:
            training_session_id (str): Training session identifier.

        Returns:
            Conversation | None: Matching conversation model or None.

        Raises:
            Exception: If the database read fails.
        """
        try:
            logging.info("Executing CRUDConversation.get_by_training_session_id")
            return await get_engine().find_one(
                Conversation,
                Conversation.training_session_id == training_session_id,
            )
        except Exception as error:
            logging.error(
                f"Error in CRUDConversation.get_by_training_session_id: {error}"
            )
            raise error

    async def get_by_conversation_id(
        self,
        *,
        conversation_id: str,
    ) -> Conversation | None:
        """Read a conversation record by external conversation identifier.

        Args:
            conversation_id (str): Eigi conversation identifier.

        Returns:
            Conversation | None: Matching conversation model or None.

        Raises:
            Exception: If the database read fails.
        """
        try:
            logging.info("Executing CRUDConversation.get_by_conversation_id")
            return await get_engine().find_one(
                Conversation,
                Conversation.conversation_id == conversation_id,
            )
        except Exception as error:
            logging.error(
                f"Error in CRUDConversation.get_by_conversation_id: {error}"
            )
            raise error

    async def update(self, *, id: str, obj_in: dict) -> Conversation | None:
        """Update an existing conversation record by identifier.

        Args:
            id (str): Conversation identifier.
            obj_in (dict): Fields to update.

        Returns:
            Conversation | None: Updated model or None when not found.

        Raises:
            HTTPException 400: If the identifier is invalid.
            Exception: If the database update fails.
        """
        try:
            logging.info("Executing CRUDConversation.update")
            conversation = await self.get_by_id(id=id)
            if conversation is None:
                logging.warning(f"No conversation found with id: {id}")
                return None

            for field, value in obj_in.items():
                setattr(conversation, field, value)
            conversation.updated_at = get_utc_now()

            await get_engine().save(conversation)
            return conversation
        except HTTPException:
            raise
        except Exception as error:
            logging.error(f"Error in CRUDConversation.update: {error}")
            raise error
