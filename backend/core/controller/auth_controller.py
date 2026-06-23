"""Controller logic for authentication-related workflows."""

from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status

from commons.auth import (
    generate_otp,
    hash_otp,
    signJWT,
    verify_hashed_otp,
    verify_password,
)
from commons.logger import logger
from core.cruds.user_crud import CRUDUser
from core.database.database import get_utc_now
from core.models.user_model import OtpPurpose, UserRole

logging = logger(__name__)


class AuthController:
    """Business orchestration for authentication flows."""

    def __init__(self) -> None:
        """Initialize CRUD dependencies for auth workflows."""
        self.crud_user = CRUDUser()

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

    async def admin_login(self, *, phone_number: str, password: str) -> dict:
        """Validate admin credentials and issue a fresh OTP challenge.

        Args:
            phone_number (str): Admin phone number used for login.
            password (str): Plain-text admin password.

        Returns:
            dict: OTP dispatch response payload.

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

            otp = generate_otp()
            otp_state = {
                "code_hash": hash_otp(otp),
                "purpose": OtpPurpose.ADMIN_LOGIN,
                "expires_at": get_utc_now() + timedelta(minutes=10),
                "requested_at": get_utc_now(),
                "attempt_count": 0,
                "attempt_window_started_at": get_utc_now(),
            }
            await self.crud_user.update(id=str(user.id), obj_in={"otp": otp_state})
            logging.info(
                f"Mock admin OTP generated on backend server for {phone_number}: {otp}"
            )

            return {
                "message": "Mock OTP generated successfully on backend server"
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
        """Verify an admin OTP and return a signed login response.

        Args:
            phone_number (str): Admin phone number associated with the OTP.
            otp (str): Plain OTP value entered by the admin.

        Returns:
            dict: Auth success payload with JWT and user profile.

        Raises:
            HTTPException: If the OTP is invalid, expired, or the user is not eligible.
        """
        try:
            logging.info("Executing AuthController.verify_admin_otp")
            user = await self.crud_user.get_by_phone_number(phone_number=phone_number)
            if user is None or user.role != UserRole.ADMIN:
                logging.warning(f"Admin user not found for phone number {phone_number}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid authentication credentials",
                )

            if not user.is_active:
                logging.warning(f"Inactive admin attempted OTP verification: {phone_number}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User is not active",
                )

            if user.otp is None or user.otp.purpose != OtpPurpose.ADMIN_LOGIN:
                logging.warning(f"No active admin OTP found for {phone_number}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No active OTP found for this user",
                )

            if self._as_utc(user.otp.expires_at) < get_utc_now():
                logging.warning(f"Expired admin OTP attempted for {phone_number}")
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
                logging.warning(f"Invalid admin OTP attempt for {phone_number}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid OTP",
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
            logging.error(f"Error in AuthController.verify_admin_otp: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )

    async def salesperson_login(self, *, email: str, password: str) -> dict:
        """Authenticate a salesperson with email and password.

        Args:
            email (str): Salesperson email address.
            password (str): Plain-text password.

        Returns:
            dict: Auth success payload with JWT and user profile.

        Raises:
            HTTPException: If the credentials are invalid or the user is inactive.
        """
        try:
            logging.info("Executing AuthController.salesperson_login")
            user = await self.crud_user.get_by_email(email=email)
            if user is None or user.role != UserRole.SALESPERSON:
                logging.warning(f"Salesperson user not found for email {email}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password",
                )

            if not user.is_active:
                logging.warning(f"Inactive salesperson attempted login: {email}")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User is not active",
                )

            if not verify_password(password, user.password_hash):
                logging.warning(f"Invalid salesperson password attempt for {email}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password",
                )

            updated_user = await self.crud_user.update(
                id=str(user.id),
                obj_in={"last_login_at": get_utc_now()},
            )
            if updated_user is None:
                logging.error(f"Failed to update salesperson login state for {email}")
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
            logging.error(f"Error in AuthController.salesperson_login: {error}")
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
