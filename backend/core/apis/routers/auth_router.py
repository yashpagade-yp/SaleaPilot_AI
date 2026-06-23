"""API routes for authentication-related operations."""

from fastapi import APIRouter, HTTPException, status

from commons.logger import logger
from core.apis.schemas.requests_schemas.auth_request import (
    AdminLoginRequest,
    AdminVerifyOtpRequest,
    ResetPasswordRequest,
    SalespersonLoginRequest,
)
from core.apis.schemas.responses_schemas.auth_response import (
    LoginResponse,
    OtpSentResponse,
)
from core.controller.auth_controller import AuthController

auth_router = APIRouter(prefix="/v1/auth", tags=["auth"])
logging = logger(__name__)


@auth_router.post(
    "/admin/login",
    status_code=status.HTTP_200_OK,
    response_model=OtpSentResponse,
)
async def admin_login(request: AdminLoginRequest) -> OtpSentResponse:
    """Start admin login by validating credentials and issuing a mock OTP.

    Args:
        request (AdminLoginRequest): Admin login payload with phone and password.

    Returns:
        OtpSentResponse: Mock OTP generation acknowledgement payload.

    Raises:
        HTTPException: If the credentials are invalid or the request fails.
    """
    try:
        logging.info("Calling POST /v1/auth/admin/login endpoint")
        response = await AuthController().admin_login(
            phone_number=request.phone_number,
            password=request.password,
        )
        return OtpSentResponse(**response)
    except HTTPException as httperror:
        logging.error(f"Error in POST /v1/auth/admin/login endpoint: {httperror}")
        raise httperror
    except Exception as error:
        logging.error(f"Error in POST /v1/auth/admin/login endpoint: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@auth_router.post(
    "/admin/verify-otp",
    status_code=status.HTTP_200_OK,
    response_model=LoginResponse,
)
async def verify_admin_otp(request: AdminVerifyOtpRequest) -> LoginResponse:
    """Verify an admin OTP and complete login.

    Args:
        request (AdminVerifyOtpRequest): Admin OTP verification payload.

    Returns:
        LoginResponse: Auth success payload with token and user profile.

    Raises:
        HTTPException: If the OTP or user state is invalid.
    """
    try:
        logging.info("Calling POST /v1/auth/admin/verify-otp endpoint")
        response = await AuthController().verify_admin_otp(
            phone_number=request.phone_number,
            otp=request.otp,
        )
        return LoginResponse(**response)
    except HTTPException as httperror:
        logging.error(
            f"Error in POST /v1/auth/admin/verify-otp endpoint: {httperror}"
        )
        raise httperror
    except Exception as error:
        logging.error(f"Error in POST /v1/auth/admin/verify-otp endpoint: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@auth_router.post(
    "/salesperson/login",
    status_code=status.HTTP_200_OK,
    response_model=LoginResponse,
)
async def salesperson_login(request: SalespersonLoginRequest) -> LoginResponse:
    """Authenticate a salesperson using email and password.

    Args:
        request (SalespersonLoginRequest): Salesperson login payload.

    Returns:
        LoginResponse: Auth success payload with token and user profile.

    Raises:
        HTTPException: If the credentials are invalid or the user is inactive.
    """
    try:
        logging.info("Calling POST /v1/auth/salesperson/login endpoint")
        response = await AuthController().salesperson_login(
            email=request.email,
            password=request.password,
        )
        return LoginResponse(**response)
    except HTTPException as httperror:
        logging.error(
            f"Error in POST /v1/auth/salesperson/login endpoint: {httperror}"
        )
        raise httperror
    except Exception as error:
        logging.error(f"Error in POST /v1/auth/salesperson/login endpoint: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@auth_router.post(
    "/reset-password",
    status_code=status.HTTP_200_OK,
    response_model=OtpSentResponse,
)
async def reset_password(request: ResetPasswordRequest) -> OtpSentResponse:
    """Start a password reset workflow placeholder.

    Args:
        request (ResetPasswordRequest): Password reset request payload.

    Returns:
        OtpSentResponse: Reset acknowledgement payload.

    Raises:
        HTTPException: Always raised until the reset flow is implemented.
    """
    try:
        logging.info("Calling POST /v1/auth/reset-password endpoint")
        response = await AuthController().reset_password(email=request.email)
        return OtpSentResponse(**response)
    except HTTPException as httperror:
        logging.error(f"Error in POST /v1/auth/reset-password endpoint: {httperror}")
        raise httperror
    except Exception as error:
        logging.error(f"Error in POST /v1/auth/reset-password endpoint: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )
