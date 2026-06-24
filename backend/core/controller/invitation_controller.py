"""Controller logic for invitation-related workflows."""

import secrets
import smtplib
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status

from commons.auth import encrypt_password
from commons.logger import logger
from core.cruds.invitation_crud import CRUDInvitation
from core.cruds.user_crud import CRUDUser
from core.database.database import get_utc_now
from core.models.invitation_model import InvitationStatus
from core.models.user_model import UserRole
from core.services.email_service import EmailService

logging = logger(__name__)


class InvitationController:
    """Business orchestration for invitation workflows."""

    def __init__(self) -> None:
        """Initialize CRUD dependencies for invitation workflows."""
        self.crud_invitation = CRUDInvitation()
        self.crud_user = CRUDUser()
        self.email_service = EmailService()

    @staticmethod
    def _generate_placeholder_phone_number() -> str:
        """Generate a unique placeholder phone number for invited salespeople.

        Keeps salesperson placeholder records compatible with the current user
        storage shape while real login identity continues to use email OTP.

        Returns:
            str: Random numeric placeholder value.
        """
        return f"9{secrets.randbelow(10**17):017d}"

    @staticmethod
    def _select_pending_invitation(invitations: list) -> object | None:
        """Return the latest pending invitation from an email's invitation set.

        Args:
            invitations (list): Invitation model instances for one email.

        Returns:
            object | None: Pending invitation or None when no active pending
            invitation exists.
        """
        pending_invitations = [
            invitation
            for invitation in invitations
            if invitation.status == InvitationStatus.PENDING
        ]
        if not pending_invitations:
            return None

        return max(pending_invitations, key=lambda invitation: invitation.created_at)

    @staticmethod
    def _as_utc(value: datetime) -> datetime:
        """Normalize a datetime value to UTC-aware form.

        Args:
            value (datetime): Datetime value loaded from persistence.

        Returns:
            datetime: UTC-aware datetime for safe comparisons.
        """
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

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
            if existing_user is not None and (
                existing_user.role != UserRole.SALESPERSON or existing_user.is_active
            ):
                logging.warning(f"Invitation attempted for existing active user email {email}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="A user with this email already exists",
                )

            existing_invitation = self._select_pending_invitation(
                await self.crud_invitation.list_by_email(email=email)
            )
            if (
                existing_invitation is not None
                and existing_invitation.expires_at > get_utc_now()
            ):
                logging.warning(f"Pending invitation already exists for email {email}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="A pending invitation already exists for this email",
                )

            if existing_user is None:
                await self.crud_user.create(
                    obj_in={
                        "first_name": first_name,
                        "last_name": last_name,
                        "email": email,
                        "phone_number": self._generate_placeholder_phone_number(),
                        "password_hash": encrypt_password(secrets.token_urlsafe(32)),
                        "role": UserRole.SALESPERSON,
                        "is_active": False,
                        "auth_metadata": {
                            "invited_via_email": True,
                        },
                    }
                )
            else:
                await self.crud_user.update(
                    id=str(existing_user.id),
                    obj_in={
                        "first_name": first_name,
                        "last_name": last_name,
                        "phone_number": (
                            existing_user.phone_number
                            or self._generate_placeholder_phone_number()
                        ),
                        "is_active": False,
                        "otp": None,
                    },
                )

            invitation = await self.crud_invitation.create(
                obj_in={
                    "email": email,
                    "first_name": first_name,
                    "last_name": last_name,
                    "role": UserRole.SALESPERSON,
                    "invited_by": invited_by,
                    "status": InvitationStatus.PENDING,
                    "token": secrets.token_urlsafe(24),
                    "expires_at": get_utc_now() + timedelta(days=7),
                }
            )

            email_body = (
                f"Hello {first_name} {last_name},\n\n"
                "You have been invited to SalesPilot AI as a salesperson.\n"
                "Your email has been approved for OTP-based salesperson login.\n"
                "Copy the invitation token below and paste it into the invitation field on the salesperson login screen:\n\n"
                f"{invitation.token}\n\n"
                "Next step:\n"
                "- open the salesperson login screen\n"
                "- paste this invitation token first\n"
                "- enter this invited email address\n"
                "- request the OTP sent to your email\n"
                "- enter the OTP to continue into your workspace\n\n"
                "Regards,\nSalesPilot AI"
            )
            self.email_service.send_email(
                to_email=email,
                subject="SalesPilot AI Invitation",
                body=email_body,
            )

            return {
                "id": str(invitation.id),
                "email": invitation.email,
                "first_name": invitation.first_name,
                "last_name": invitation.last_name,
                "role": invitation.role,
                "status": invitation.status,
                "invited_by": invitation.invited_by,
                "expires_at": invitation.expires_at,
                "accepted_at": invitation.accepted_at,
            }
        except HTTPException:
            raise
        except smtplib.SMTPException as error:
            logging.error(f"Error in InvitationController.send_invitation email send: {error}")
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Invitation created but email delivery failed",
            )
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
    ) -> dict:
        """Validate an invitation token and explain the salesperson's next step.

        Args:
            token (str): Invitation token.

        Returns:
            dict: Invitation acknowledgement response payload.

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

            if invitation.status == InvitationStatus.CANCELLED:
                logging.warning(f"Cancelled invitation attempted: {invitation.id}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invitation is no longer valid",
                )

            if self._as_utc(invitation.expires_at) < get_utc_now():
                logging.warning(f"Expired invitation attempted: {invitation.id}")
                await self.crud_invitation.update(
                    id=str(invitation.id),
                    obj_in={"status": InvitationStatus.EXPIRED},
                )
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invitation has expired",
                )

            return {
                "message": "Invitation token matched successfully",
                "email": invitation.email,
                "status": invitation.status,
                "next_step": (
                    "Use this same invited email address to request the real "
                    "salesperson login OTP."
                ),
            }
        except HTTPException:
            raise
        except Exception as error:
            logging.error(f"Error in InvitationController.accept_invitation: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )
