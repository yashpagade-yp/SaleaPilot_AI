"""Controller logic for invitation-related workflows."""

import re
import secrets
from os import getenv
from datetime import datetime, timedelta, timezone
from urllib.parse import quote

from fastapi import HTTPException, status

from commons.auth import encrypt_password
from commons.logger import logger
from core.cruds.invitation_crud import CRUDInvitation
from core.cruds.user_crud import CRUDUser
from core.database.database import get_utc_now
from core.models.invitation_model import InvitationStatus
from core.models.user_model import UserRole
from core.services.email_helper import EmailDeliveryError, send_email
from core.services.email_template_generator import build_salesperson_invitation_email

logging = logger(__name__)


class InvitationController:
    """Business orchestration for invitation workflows."""

    def __init__(self) -> None:
        """Initialize CRUD dependencies for invitation workflows."""
        self.crud_invitation = CRUDInvitation()
        self.crud_user = CRUDUser()

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

    @staticmethod
    def _should_expose_dev_delivery_preview() -> bool:
        """Decide whether development-only invitation previews may be returned.

        Returns:
            bool: True when the app is outside production.
        """
        app_env = getenv("APP_ENV", "development").strip().lower()
        return app_env != "production"

    @staticmethod
    def _build_accept_invitation_url(*, email: str, token: str) -> str:
        """Build the frontend accept-invitation URL for one invite.

        Args:
            email (str): Invited salesperson email address.
            token (str): Invitation token stored in the backend.

        Returns:
            str: Absolute frontend URL for the accept-invitation page.
        """
        frontend_base_url = getenv("FRONTEND_BASE_URL", "http://localhost:5173").rstrip("/")
        return (
            f"{frontend_base_url}/accept-invitation"
            f"?email={quote(email, safe='')}&invitation_token={quote(token, safe='')}"
        )

    @staticmethod
    def _derive_name_parts_from_email(email: str) -> tuple[str, str]:
        """Derive safe placeholder name parts from an email address.

        Args:
            email (str): Invited salesperson email address.

        Returns:
            tuple[str, str]: First and last name placeholders for persistence.
        """
        local_part = email.split("@", maxsplit=1)[0]
        tokens = [
            token.capitalize()
            for token in re.split(r"[^A-Za-z0-9]+", local_part)
            if token
        ]

        if len(tokens) >= 2:
            return tokens[0][:50], " ".join(tokens[1:])[:50]

        if len(tokens) == 1:
            first_name = tokens[0][:50]
            if len(first_name) < 2:
                first_name = f"{first_name}x"
            return first_name, "Salesperson"

        return "Sales", "Person"

    async def send_invitation(
        self,
        *,
        email: str,
        first_name: str | None,
        last_name: str | None,
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
            resolved_first_name = first_name
            resolved_last_name = last_name
            if not resolved_first_name or not resolved_last_name:
                resolved_first_name, resolved_last_name = (
                    self._derive_name_parts_from_email(email)
                )

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
                and self._as_utc(existing_invitation.expires_at) > get_utc_now()
            ):
                logging.warning(f"Pending invitation already exists for email {email}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="A pending invitation already exists for this email",
                )

            if existing_user is None:
                await self.crud_user.create(
                    obj_in={
                        "first_name": resolved_first_name,
                        "last_name": resolved_last_name,
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
                        "first_name": resolved_first_name,
                        "last_name": resolved_last_name,
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
                    "first_name": resolved_first_name,
                    "last_name": resolved_last_name,
                    "role": UserRole.SALESPERSON,
                    "invited_by": invited_by,
                    "status": InvitationStatus.PENDING,
                    "token": secrets.token_urlsafe(24),
                    "expires_at": get_utc_now() + timedelta(days=7),
                }
            )

            accept_invitation_url = self._build_accept_invitation_url(
                email=email,
                token=invitation.token,
            )

            email_template = build_salesperson_invitation_email(
                name=f"{resolved_first_name} {resolved_last_name}".strip(),
                invitation_token=invitation.token,
                accept_invitation_url=accept_invitation_url,
            )
            await send_email(
                subject=email_template["subject"],
                to_email=email,
                text=email_template["text"],
                html=email_template["html"],
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
                "delivery_channel": "email",
                "dev_invitation_token": (
                    invitation.token
                    if self._should_expose_dev_delivery_preview()
                    else None
                ),
            }
        except HTTPException:
            raise
        except EmailDeliveryError as error:
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
