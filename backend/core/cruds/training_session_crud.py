"""CRUD operations for training session records."""

from fastapi import HTTPException, status

from commons.logger import logger
from core.database.database import get_engine, get_utc_now, parse_object_id
from core.models.training_session_model import TrainingSession, TrainingSessionStatus

logging = logger(__name__)


class CRUDTrainingSession:
    """Database access layer for training session records."""

    async def create(self, *, obj_in: dict) -> TrainingSession:
        """Create a new training session record.

        Args:
            obj_in (dict): Training session creation payload.

        Returns:
            TrainingSession: Created training session model instance.

        Raises:
            Exception: If the database write fails.
        """
        try:
            logging.info("Executing CRUDTrainingSession.create")
            training_session = TrainingSession(**obj_in)
            await get_engine().save(training_session)
            return training_session
        except Exception as error:
            logging.error(f"Error in CRUDTrainingSession.create: {error}")
            raise error

    async def get_by_id(self, *, id: str) -> TrainingSession | None:
        """Read a training session record by unique identifier.

        Args:
            id (str): Training session identifier.

        Returns:
            TrainingSession | None: Matching training session model or None.

        Raises:
            HTTPException 400: If the identifier is invalid.
            Exception: If the database read fails.
        """
        try:
            logging.info("Executing CRUDTrainingSession.get_by_id")
            return await get_engine().find_one(
                TrainingSession,
                TrainingSession.id == parse_object_id(id),
            )
        except ValueError as error:
            logging.warning(f"Invalid training session id received: {id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(error),
            ) from error
        except Exception as error:
            logging.error(f"Error in CRUDTrainingSession.get_by_id: {error}")
            raise error

    async def list_by_user_id(self, *, user_id: str) -> list[TrainingSession]:
        """List training sessions created by one salesperson.

        Args:
            user_id (str): Salesperson user identifier.

        Returns:
            list[TrainingSession]: Matching training session records.

        Raises:
            Exception: If the database read fails.
        """
        try:
            logging.info("Executing CRUDTrainingSession.list_by_user_id")
            return await get_engine().find(
                TrainingSession,
                TrainingSession.user_id == user_id,
            )
        except Exception as error:
            logging.error(f"Error in CRUDTrainingSession.list_by_user_id: {error}")
            raise error

    async def get_by_conversation_id(
        self,
        *,
        conversation_id: str,
    ) -> TrainingSession | None:
        """Read a training session record by Eigi conversation identifier.

        Args:
            conversation_id (str): Eigi conversation identifier.

        Returns:
            TrainingSession | None: Matching training session model or None.

        Raises:
            Exception: If the database read fails.
        """
        try:
            logging.info("Executing CRUDTrainingSession.get_by_conversation_id")
            return await get_engine().find_one(
                TrainingSession,
                TrainingSession.conversation_id == conversation_id,
            )
        except Exception as error:
            logging.error(
                f"Error in CRUDTrainingSession.get_by_conversation_id: {error}"
            )
            raise error

    async def list_by_status(
        self,
        *,
        status: TrainingSessionStatus,
    ) -> list[TrainingSession]:
        """List training sessions filtered by lifecycle status.

        Args:
            status (TrainingSessionStatus): Training-session status to filter by.

        Returns:
            list[TrainingSession]: Matching training session records.

        Raises:
            Exception: If the database read fails.
        """
        try:
            logging.info("Executing CRUDTrainingSession.list_by_status")
            return await get_engine().find(
                TrainingSession,
                TrainingSession.status == status,
            )
        except Exception as error:
            logging.error(f"Error in CRUDTrainingSession.list_by_status: {error}")
            raise error

    async def update(self, *, id: str, obj_in: dict) -> TrainingSession | None:
        """Update an existing training session record by identifier.

        Args:
            id (str): Training session identifier.
            obj_in (dict): Fields to update.

        Returns:
            TrainingSession | None: Updated model or None when not found.

        Raises:
            HTTPException 400: If the identifier is invalid.
            Exception: If the database update fails.
        """
        try:
            logging.info("Executing CRUDTrainingSession.update")
            training_session = await self.get_by_id(id=id)
            if training_session is None:
                logging.warning(f"No training session found with id: {id}")
                return None

            for field, value in obj_in.items():
                setattr(training_session, field, value)
            training_session.updated_at = get_utc_now()

            await get_engine().save(training_session)
            return training_session
        except HTTPException:
            raise
        except Exception as error:
            logging.error(f"Error in CRUDTrainingSession.update: {error}")
            raise error
