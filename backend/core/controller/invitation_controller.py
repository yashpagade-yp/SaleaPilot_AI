"""Controller logic for invitation-related workflows."""

import secrets
from datetime import timedelta

from fastapi import HTTPException, status

from commons.auth import encrypt_password
from commons.logger import logger
from core.cruds.invitation_crud import CRUDInvitation
from core.cruds.user_crud import CRUDUser
from core.database.database import get_utc_now
from core.models.invitation_model import InvitationStatus
from core.models.user_model import UserRole

logging = logger(__name__)


class InvitationController:
    """Business orchestration for invitation workflows."""

    def __init__(self) -> None:
        """Initialize CRUD dependencies for invitation workflows."""
        self.crud_invitation = CRUDInvitation()
        self.crud_user = CRUDUser()

    async def send_invitation(
        self,
        *,
        email: str,
        first_name: str,
        last_name: str,
        invited_by: str,
    ) -> dict:
        """Create a new pending invitation for a salesperson.

        Args:
            email (str): Invited salesperson email address.
            first_name (str): Invited salesperson first name.
            last_name (str): Invited salesperson last name.
            invited_by (str): Admin user identifier creating the invitation.

        Returns:
            dict: Invitation response payload.

        Raises:
            HTTPException: If a pending invitation or active user already exists.
        """
        try:
            logging.info("Executing InvitationController.send_invitation")
            existing_user = await self.crud_user.get_by_email(email=email)
            if existing_user is not None:
                logging.warning(f"Invitation attempted for existing user email {email}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="A user with this email already exists",
                )

            existing_invitation = await self.crud_invitation.get_by_email(email=email)
            if (
                existing_invitation is not None
                and existing_invitation.status == InvitationStatus.PENDING
                and existing_invitation.expires_at > get_utc_now()
            ):
                logging.warning(f"Pending invitation already exists for email {email}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="A pending invitation already exists for this email",
                )

            invitation = await self.crud_invitation.create(
                obj_in={
                    "email": email,
                    "role": UserRole.SALESPERSON,
                    "invited_by": invited_by,
                    "status": InvitationStatus.PENDING,
                    "token": secrets.token_urlsafe(24),
                    "expires_at": get_utc_now() + timedelta(days=7),
                }
            )

            return {
                "id": str(invitation.id),
                "email": invitation.email,
                "role": invitation.role,
                "status": invitation.status,
                "invited_by": invitation.invited_by,
                "expires_at": invitation.expires_at,
                "accepted_at": invitation.accepted_at,
            }
        except HTTPException:
            raise
        except Exception as error:
            logging.error(f"Error in InvitationController.send_invitation: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )

    async def accept_invitation(
        self,
        *,
        token: str,
        first_name: str,
        last_name: str,
        password: str,
    ) -> dict:
        """Accept a pending invitation and create a salesperson account.

        Args:
            token (str): Invitation token.
            first_name (str): Confirmed salesperson first name.
            last_name (str): Confirmed salesperson last name.
            password (str): Plain-text password selected by the salesperson.

        Returns:
            dict: Invitation acceptance response payload.

        Raises:
            HTTPException: If the invitation is invalid, expired, or already used.
        """
        try:
            logging.info("Executing InvitationController.accept_invitation")
            invitation = await self.crud_invitation.get_by_token(token=token)
            if invitation is None:
                logging.warning("Invitation acceptance attempted with unknown token")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Invitation not found",
                )

            if invitation.status != InvitationStatus.PENDING:
                logging.warning(f"Invitation is not pending: {invitation.id}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invitation is no longer valid",
                )

            if invitation.expires_at < get_utc_now():
                logging.warning(f"Expired invitation attempted: {invitation.id}")
                await self.crud_invitation.update(
                    id=str(invitation.id),
                    obj_in={"status": InvitationStatus.EXPIRED},
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invitation has expired",
                )

            existing_user = await self.crud_user.get_by_email(email=invitation.email)
            if existing_user is not None:
                logging.warning(
                    f"Invitation acceptance attempted for existing user {invitation.email}"
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="A user with this email already exists",
                )

            user = await self.crud_user.create(
                obj_in={
                    "first_name": first_name,
                    "last_name": last_name,
                    "email": invitation.email,
                    "password_hash": encrypt_password(password),
                    "role": UserRole.SALESPERSON,
                    "is_active": True,
                }
            )

            await self.crud_invitation.update(
                id=str(invitation.id),
                obj_in={
                    "status": InvitationStatus.ACCEPTED,
                    "accepted_at": get_utc_now(),
                },
            )

            return {
                "message": "Invitation accepted successfully",
                "user_id": str(user.id),
            }
        except HTTPException:
            raise
        except Exception as error:
            logging.error(f"Error in InvitationController.accept_invitation: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )
