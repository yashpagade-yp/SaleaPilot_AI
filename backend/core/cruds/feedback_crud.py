"""CRUD operations for feedback records."""

from fastapi import HTTPException, status

from commons.logger import logger
from core.database.database import get_engine, get_utc_now, parse_object_id
from core.models.feedback_model import Feedback

logging = logger(__name__)


class CRUDFeedback:
    """Database access layer for feedback records."""

    async def create(self, *, obj_in: dict) -> Feedback:
        """Create a new feedback record.

        Args:
            obj_in (dict): Feedback creation payload.

        Returns:
            Feedback: Created feedback model instance.

        Raises:
            Exception: If the database write fails.
        """
        try:
            logging.info("Executing CRUDFeedback.create")
            feedback = Feedback(**obj_in)
            await get_engine().save(feedback)
            return feedback
        except Exception as error:
            logging.error(f"Error in CRUDFeedback.create: {error}")
            raise error

    async def get_by_id(self, *, id: str) -> Feedback | None:
        """Read a feedback record by unique identifier.

        Args:
            id (str): Feedback identifier.

        Returns:
            Feedback | None: Matching feedback model or None.

        Raises:
            HTTPException 400: If the identifier is invalid.
            Exception: If the database read fails.
        """
        try:
            logging.info("Executing CRUDFeedback.get_by_id")
            return await get_engine().find_one(
                Feedback,
                Feedback.id == parse_object_id(id),
            )
        except ValueError as error:
            logging.warning(f"Invalid feedback id received: {id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(error),
            ) from error
        except Exception as error:
            logging.error(f"Error in CRUDFeedback.get_by_id: {error}")
            raise error

    async def get_by_training_session_id(
        self,
        *,
        training_session_id: str,
    ) -> Feedback | None:
        """Read a feedback record by training session identifier.

        Args:
            training_session_id (str): Training session identifier.

        Returns:
            Feedback | None: Matching feedback model or None.

        Raises:
            Exception: If the database read fails.
        """
        try:
            logging.info("Executing CRUDFeedback.get_by_training_session_id")
            return await get_engine().find_one(
                Feedback,
                Feedback.training_session_id == training_session_id,
            )
        except Exception as error:
            logging.error(
                f"Error in CRUDFeedback.get_by_training_session_id: {error}"
            )
            raise error

    async def list_by_user_id(self, *, user_id: str) -> list[Feedback]:
        """List feedback records belonging to one salesperson.

        Args:
            user_id (str): Salesperson user identifier.

        Returns:
            list[Feedback]: Matching feedback records.

        Raises:
            Exception: If the database read fails.
        """
        try:
            logging.info("Executing CRUDFeedback.list_by_user_id")
            return await get_engine().find(Feedback, Feedback.user_id == user_id)
        except Exception as error:
            logging.error(f"Error in CRUDFeedback.list_by_user_id: {error}")
            raise error

    async def update(self, *, id: str, obj_in: dict) -> Feedback | None:
        """Update an existing feedback record by identifier.

        Args:
            id (str): Feedback identifier.
            obj_in (dict): Fields to update.

        Returns:
            Feedback | None: Updated model or None when not found.

        Raises:
            HTTPException 400: If the identifier is invalid.
            Exception: If the database update fails.
        """
        try:
            logging.info("Executing CRUDFeedback.update")
            feedback = await self.get_by_id(id=id)
            if feedback is None:
                logging.warning(f"No feedback found with id: {id}")
                return None

            for field, value in obj_in.items():
                setattr(feedback, field, value)
            feedback.updated_at = get_utc_now()

            await get_engine().save(feedback)
            return feedback
        except HTTPException:
            raise
        except Exception as error:
            logging.error(f"Error in CRUDFeedback.update: {error}")
            raise error
