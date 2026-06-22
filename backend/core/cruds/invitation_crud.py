"""CRUD operations for invitation records."""

from fastapi import HTTPException, status

from commons.logger import logger
from core.database.database import get_engine, get_utc_now, parse_object_id
from core.models.invitation_model import Invitation, InvitationStatus

logging = logger(__name__)


class CRUDInvitation:
    """Database access layer for invitation records."""

    async def create(self, *, obj_in: dict) -> Invitation:
        """Create a new invitation record.

        Args:
            obj_in (dict): Invitation creation payload.

        Returns:
            Invitation: Created invitation model instance.

        Raises:
            Exception: If the database write fails.
        """
        try:
            logging.info("Executing CRUDInvitation.create")
            invitation = Invitation(**obj_in)
            await get_engine().save(invitation)
            return invitation
        except Exception as error:
            logging.error(f"Error in CRUDInvitation.create: {error}")
            raise error

    async def get_by_id(self, *, id: str) -> Invitation | None:
        """Read an invitation record by unique identifier.

        Args:
            id (str): Invitation identifier.

        Returns:
            Invitation | None: Matching invitation model or None.

        Raises:
            HTTPException 400: If the identifier is invalid.
            Exception: If the database read fails.
        """
        try:
            logging.info("Executing CRUDInvitation.get_by_id")
            return await get_engine().find_one(
                Invitation,
                Invitation.id == parse_object_id(id),
            )
        except ValueError as error:
            logging.warning(f"Invalid invitation id received: {id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(error),
            ) from error
        except Exception as error:
            logging.error(f"Error in CRUDInvitation.get_by_id: {error}")
            raise error

    async def get_by_email(self, *, email: str) -> Invitation | None:
        """Read an invitation record for an email address.

        Args:
            email (str): Invited salesperson email address.

        Returns:
            Invitation | None: Matching invitation model or None.

        Raises:
            Exception: If the database read fails.
        """
        try:
            logging.info("Executing CRUDInvitation.get_by_email")
            return await get_engine().find_one(Invitation, Invitation.email == email)
        except Exception as error:
            logging.error(f"Error in CRUDInvitation.get_by_email: {error}")
            raise error

    async def get_by_token(self, *, token: str) -> Invitation | None:
        """Read an invitation record by acceptance token.

        Args:
            token (str): Invitation token.

        Returns:
            Invitation | None: Matching invitation model or None.

        Raises:
            Exception: If the database read fails.
        """
        try:
            logging.info("Executing CRUDInvitation.get_by_token")
            return await get_engine().find_one(Invitation, Invitation.token == token)
        except Exception as error:
            logging.error(f"Error in CRUDInvitation.get_by_token: {error}")
            raise error

    async def list_pending(self) -> list[Invitation]:
        """List all pending invitation records.

        Returns:
            list[Invitation]: Pending invitation records.

        Raises:
            Exception: If the database read fails.
        """
        try:
            logging.info("Executing CRUDInvitation.list_pending")
            return await get_engine().find(
                Invitation,
                Invitation.status == InvitationStatus.PENDING,
            )
        except Exception as error:
            logging.error(f"Error in CRUDInvitation.list_pending: {error}")
            raise error

    async def update(self, *, id: str, obj_in: dict) -> Invitation | None:
        """Update an existing invitation record by identifier.

        Args:
            id (str): Invitation identifier.
            obj_in (dict): Fields to update.

        Returns:
            Invitation | None: Updated model or None when not found.

        Raises:
            HTTPException 400: If the identifier is invalid.
            Exception: If the database update fails.
        """
        try:
            logging.info("Executing CRUDInvitation.update")
            invitation = await self.get_by_id(id=id)
            if invitation is None:
                logging.warning(f"No invitation found with id: {id}")
                return None

            for field, value in obj_in.items():
                setattr(invitation, field, value)
            invitation.updated_at = get_utc_now()

            await get_engine().save(invitation)
            return invitation
        except HTTPException:
            raise
        except Exception as error:
            logging.error(f"Error in CRUDInvitation.update: {error}")
            raise error
