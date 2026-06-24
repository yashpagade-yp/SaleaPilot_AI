"""Controller logic for authentication-related workflows."""

from datetime import datetime, timedelta, timezone
import smtplib

from fastapi import HTTPException, status

from commons.auth import (
    generate_otp,
    hash_otp,
    signJWT,
    verify_hashed_otp,
    verify_password,
)
from commons.logger import logger
from core.cruds.invitation_crud import CRUDInvitation
from core.cruds.user_crud import CRUDUser
from core.database.database import get_utc_now
from core.models.invitation_model import InvitationStatus
from core.models.user_model import OtpPurpose, UserRole
from core.services.email_service import EmailService

logging = logger(__name__)


class AuthController:
    """Business orchestration for authentication flows."""

    def __init__(self) -> None:
        """Initialize CRUD dependencies for auth workflows."""
        self.crud_user = CRUDUser()
        self.crud_invitation = CRUDInvitation()
        self.email_service = EmailService()

    @staticmethod
    def _serialize_user_profile(user) -> dict:
        """Convert a user model into the auth response shape.

        Args:
            user: Persisted user model instance.

        Returns:
            dict: User profile payload matching auth response schemas.
        """
        return {
            "id": str(user.id),
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "phone_number": user.phone_number,
            "role": user.role,
            "is_active": user.is_active,
        }

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

    async def _get_latest_pending_invitation(self, *, email: str):
        """Return the latest pending invitation for one salesperson email.

        Args:
            email (str): Salesperson email address.

        Returns:
            Invitation | None: Pending invitation or None when none exists.
        """
        invitations = await self.crud_invitation.list_by_email(email=email)
        pending_invitations = [
            invitation
            for invitation in invitations
            if invitation.status == InvitationStatus.PENDING
        ]
        if not pending_invitations:
            return None

        return max(pending_invitations, key=lambda invitation: invitation.created_at)

    async def _get_valid_invitation_for_token(
        self,
        *,
        token: str,
        email: str | None = None,
    ):
        """Return a valid invitation record for one invitation token.

        Accepts invitations that are still pending or already accepted so the
        same invited salesperson can continue using the login flow.

        Args:
            token (str): Invitation token copied from the invitation email.
            email (str | None): Optional invited email to cross-check with the token.

        Returns:
            Invitation: Matching valid invitation record.

        Raises:
            HTTPException: If the token is unknown, mismatched, expired, or cancelled.
        """
        invitation = await self.crud_invitation.get_by_token(token=token)
        if invitation is None:
            logging.warning("Salesperson OTP request attempted with unknown invitation token")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invitation token not found",
            )

        if email is not None and invitation.email != email:
            logging.warning(
                f"Invitation token email mismatch for requested salesperson email {email}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invitation token does not match this email",
            )

        if invitation.status == InvitationStatus.CANCELLED:
            logging.warning(f"Cancelled invitation token attempted for email {invitation.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invitation is no longer valid",
            )

        if self._as_utc(invitation.expires_at) < get_utc_now():
            logging.warning(f"Expired invitation token attempted for email {invitation.email}")
            await self.crud_invitation.update(
                id=str(invitation.id),
                obj_in={"status": InvitationStatus.EXPIRED},
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invitation has expired",
            )

        if invitation.status not in (
            InvitationStatus.PENDING,
            InvitationStatus.ACCEPTED,
        ):
            logging.warning(
                f"Invitation token attempted with unsupported status {invitation.status}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invitation is no longer valid",
            )

        return invitation

    async def admin_login(self, *, phone_number: str, password: str) -> dict:
        """Validate admin credentials and return a signed login response.

        Args:
            phone_number (str): Admin phone number used for login.
            password (str): Plain-text admin password.

        Returns:
            dict: Auth success payload with JWT and user profile.

        Raises:
            HTTPException: If the admin credentials are invalid or the user is inactive.
        """
        try:
            logging.info("Executing AuthController.admin_login")
            user = await self.crud_user.get_by_phone_number(phone_number=phone_number)
            if user is None or user.role != UserRole.ADMIN:
                logging.warning(f"Admin user not found for phone number {phone_number}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid phone number or password",
                )

            if not user.is_active:
                logging.warning(f"Inactive admin attempted login: {phone_number}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User is not active",
                )

            if not verify_password(password, user.password_hash):
                logging.warning(f"Invalid admin password attempt for {phone_number}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid phone number or password",
                )

            updated_user = await self.crud_user.update(
                id=str(user.id),
                obj_in={
                    "otp": None,
                    "last_login_at": get_utc_now(),
                },
            )
            if updated_user is None:
                logging.error(f"Failed to update admin login state for {phone_number}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to complete login",
                )

            return {
                "access_token": signJWT(user_role=updated_user.role, id=str(updated_user.id)),
                "token_type": "bearer",
                "user": self._serialize_user_profile(updated_user),
                "last_login_at": updated_user.last_login_at,
            }
        except HTTPException:
            raise
        except Exception as error:
            logging.error(f"Error in AuthController.admin_login: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )

    async def verify_admin_otp(self, *, phone_number: str, otp: str) -> dict:
        """Reject deprecated admin OTP verification requests.

        Args:
            phone_number (str): Admin phone number associated with the OTP.
            otp (str): Plain OTP value entered by the admin.

        Returns:
            dict: This method does not return successfully.

        Raises:
            HTTPException: Always raised because admin OTP is no longer supported.
        """
        logging.info("Executing AuthController.verify_admin_otp")
        logging.warning(
            f"Deprecated admin OTP verification attempted for phone number {phone_number}"
        )
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Admin OTP login is no longer supported",
        )

    async def salesperson_request_otp(
        self,
        *,
        invitation_token: str,
        email: str,
    ) -> dict:
        """Validate an invitation token and email an OTP for an invited salesperson.

        Args:
            invitation_token (str): Invitation token copied from the invitation email.
            email (str): Invited salesperson email address.

        Returns:
            dict: OTP dispatch acknowledgement payload.

        Raises:
            HTTPException: If the email is not eligible for salesperson login.
        """
        try:
            logging.info("Executing AuthController.salesperson_request_otp")
            await self._get_valid_invitation_for_token(
                token=invitation_token,
                email=email,
            )
            user = await self.crud_user.get_by_email(email=email)
            if user is None or user.role != UserRole.SALESPERSON:
                logging.warning(f"Salesperson user not found for email {email}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No invited salesperson account found for this email",
                )

            pending_invitation = await self._get_latest_pending_invitation(email=email)
            if pending_invitation is not None and self._as_utc(pending_invitation.expires_at) < get_utc_now():
                logging.warning(f"Expired pending invitation encountered for email {email}")
                await self.crud_invitation.update(
                    id=str(pending_invitation.id),
                    obj_in={"status": InvitationStatus.EXPIRED},
                )
                pending_invitation = None

            if not user.is_active and pending_invitation is None:
                logging.warning(f"Salesperson email is not currently invited: {email}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="This salesperson email is not eligible for OTP login",
                )

            otp = generate_otp()
            updated_user = await self.crud_user.update(
                id=str(user.id),
                obj_in={
                    "otp": {
                        "code_hash": hash_otp(otp),
                        "purpose": OtpPurpose.SALESPERSON_LOGIN,
                        "expires_at": get_utc_now() + timedelta(minutes=10),
                        "requested_at": get_utc_now(),
                        "attempt_count": 0,
                        "attempt_window_started_at": get_utc_now(),
                    }
                },
            )
            if updated_user is None:
                logging.error(f"Failed to persist salesperson OTP state for {email}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create OTP challenge",
                )

            self.email_service.send_email(
                to_email=email,
                subject="SalesPilot AI Login OTP",
                body=(
                    "Your SalesPilot AI login OTP is:\n\n"
                    f"{otp}\n\n"
                    "This OTP expires in 10 minutes."
                ),
            )

            return {
                "message": "Invitation token verified. OTP sent successfully to salesperson email",
            }
        except HTTPException:
            raise
        except smtplib.SMTPException as error:
            logging.error(
                f"Error in AuthController.salesperson_request_otp email send: {error}"
            )
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Failed to deliver salesperson OTP email",
            )
        except Exception as error:
            logging.error(f"Error in AuthController.salesperson_request_otp: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )

    async def salesperson_verify_otp(self, *, email: str, otp: str) -> dict:
        """Verify a salesperson email OTP and return a signed login response.

        Args:
            email (str): Invited salesperson email address.
            otp (str): Plain OTP value entered by the salesperson.

        Returns:
            dict: Auth success payload with JWT and user profile.

        Raises:
            HTTPException: If the email or OTP is invalid, expired, or ineligible.
        """
        try:
            logging.info("Executing AuthController.salesperson_verify_otp")
            user = await self.crud_user.get_by_email(email=email)
            if user is None or user.role != UserRole.SALESPERSON:
                logging.warning(f"Salesperson user not found for email {email}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No invited salesperson account found for this email",
                )

            pending_invitation = await self._get_latest_pending_invitation(email=email)
            if pending_invitation is not None and self._as_utc(pending_invitation.expires_at) < get_utc_now():
                logging.warning(f"Expired pending invitation encountered for email {email}")
                await self.crud_invitation.update(
                    id=str(pending_invitation.id),
                    obj_in={"status": InvitationStatus.EXPIRED},
                )
                pending_invitation = None

            if not user.is_active and pending_invitation is None:
                logging.warning(f"Salesperson email is not currently invited: {email}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="This salesperson email is not eligible for OTP login",
                )

            if user.otp is None or user.otp.purpose != OtpPurpose.SALESPERSON_LOGIN:
                logging.warning(f"No active salesperson OTP found for {email}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No active OTP found for this email",
                )

            if self._as_utc(user.otp.expires_at) < get_utc_now():
                logging.warning(f"Expired salesperson OTP attempted for {email}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="OTP has expired",
                )

            if not verify_hashed_otp(otp, user.otp.code_hash):
                attempt_count = min(user.otp.attempt_count + 1, 5)
                await self.crud_user.update(
                    id=str(user.id),
                    obj_in={
                        "otp": {
                            "code_hash": user.otp.code_hash,
                            "purpose": user.otp.purpose,
                            "expires_at": user.otp.expires_at,
                            "requested_at": user.otp.requested_at,
                            "attempt_count": attempt_count,
                            "attempt_window_started_at": user.otp.attempt_window_started_at,
                        }
                    },
                )
                logging.warning(f"Invalid salesperson OTP attempt for {email}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid OTP",
                )

            updated_user = await self.crud_user.update(
                id=str(user.id),
                obj_in={
                    "otp": None,
                    "is_active": True,
                    "last_login_at": get_utc_now(),
                },
            )
            if updated_user is None:
                logging.error(f"Failed to update salesperson login state for {email}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to complete login",
                )

            if pending_invitation is not None:
                await self.crud_invitation.update(
                    id=str(pending_invitation.id),
                    obj_in={
                        "status": InvitationStatus.ACCEPTED,
                        "accepted_at": get_utc_now(),
                    },
                )

            return {
                "access_token": signJWT(user_role=updated_user.role, id=str(updated_user.id)),
                "token_type": "bearer",
                "user": self._serialize_user_profile(updated_user),
                "last_login_at": updated_user.last_login_at,
            }
        except HTTPException:
            raise
        except Exception as error:
            logging.error(f"Error in AuthController.salesperson_verify_otp: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )

    async def reset_password(self, *, email: str) -> dict:
        """Prepare a password reset challenge for an existing user.

        Args:
            email (str): Email address requesting password reset.

        Returns:
            dict: Reset request acknowledgement payload.

        Raises:
            HTTPException: If the user is not found.
        """
        logging.info("Executing AuthController.reset_password")
        logging.warning("Password reset flow is deferred for a later phase")
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Password reset flow will be implemented later",
        )
