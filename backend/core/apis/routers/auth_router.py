"""API routes for authentication-related operations."""

from fastapi import APIRouter, HTTPException, status

from commons.logger import logger
from core.apis.schemas.requests_schemas.auth_request import (
    AdminLoginRequest,
    ResetPasswordRequest,
    SalespersonCompleteProfileRequest,
    SalespersonOtpRequest,
    SalespersonVerifyOtpRequest,
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
    response_model=LoginResponse,
)
async def admin_login(request: AdminLoginRequest) -> LoginResponse:
    """Authenticate an admin directly with phone number and password.

    Args:
        request (AdminLoginRequest): Admin login payload with phone and password.

    Returns:
        LoginResponse: Auth success payload with token and user profile.

    Raises:
        HTTPException: If the credentials are invalid or the request fails.
    """
    try:
        logging.info("Calling POST /v1/auth/admin/login endpoint")
        response = await AuthController().admin_login(
            phone_number=request.phone_number,
            password=request.password,
        )
        return LoginResponse(**response)
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
    "/salesperson/request-otp",
    status_code=status.HTTP_200_OK,
    response_model=OtpSentResponse,
)
async def salesperson_request_otp(request: SalespersonOtpRequest) -> OtpSentResponse:
    """Start salesperson login by validating the invitation token and sending a real email OTP.

    Args:
        request (SalespersonOtpRequest): Salesperson token and email payload.

    Returns:
        OtpSentResponse: OTP dispatch acknowledgement payload.

    Raises:
        HTTPException: If the email is ineligible or OTP delivery fails.
    """
    try:
        logging.info("Calling POST /v1/auth/salesperson/request-otp endpoint")
        response = await AuthController().salesperson_request_otp(
            invitation_token=request.invitation_token,
            email=request.email,
        )
        return OtpSentResponse(**response)
    except HTTPException as httperror:
        logging.error(
            "Error in POST /v1/auth/salesperson/request-otp endpoint: "
            f"{httperror}"
        )
        raise httperror
    except Exception as error:
        logging.error(
            f"Error in POST /v1/auth/salesperson/request-otp endpoint: {error}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@auth_router.post(
    "/salesperson/verify-otp",
    status_code=status.HTTP_200_OK,
    response_model=LoginResponse,
)
async def salesperson_verify_otp(
    request: SalespersonVerifyOtpRequest,
) -> LoginResponse:
    """Verify salesperson OTP and complete email-based login.

    Args:
        request (SalespersonVerifyOtpRequest): Salesperson OTP verification payload.

    Returns:
        LoginResponse: Auth success payload with token and user profile.

    Raises:
        HTTPException: If the OTP or user state is invalid.
    """
    try:
        logging.info("Calling POST /v1/auth/salesperson/verify-otp endpoint")
        response = await AuthController().salesperson_verify_otp(
            email=request.email,
            otp=request.otp,
        )
        return LoginResponse(**response)
    except HTTPException as httperror:
        logging.error(
            "Error in POST /v1/auth/salesperson/verify-otp endpoint: "
            f"{httperror}"
        )
        raise httperror
    except Exception as error:
        logging.error(
            f"Error in POST /v1/auth/salesperson/verify-otp endpoint: {error}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@auth_router.post(
    "/salesperson/complete-profile",
    status_code=status.HTTP_200_OK,
    response_model=LoginResponse,
)
async def salesperson_complete_profile(
    request: SalespersonCompleteProfileRequest,
) -> LoginResponse:
    """Complete salesperson onboarding after invitation acceptance.

    Args:
        request (SalespersonCompleteProfileRequest): Salesperson onboarding payload.

    Returns:
        LoginResponse: Auth success payload with token and user profile.

    Raises:
        HTTPException: If the invitation, OTP, or profile payload is invalid.
    """
    try:
        logging.info("Calling POST /v1/auth/salesperson/complete-profile endpoint")
        response = await AuthController().salesperson_complete_profile(
            invitation_token=request.invitation_token,
            email=request.email,
            first_name=request.first_name,
            last_name=request.last_name,
            otp=request.otp,
            password=request.password,
        )
        return LoginResponse(**response)
    except HTTPException as httperror:
        logging.error(
            "Error in POST /v1/auth/salesperson/complete-profile endpoint: "
            f"{httperror}"
        )
        raise httperror
    except Exception as error:
        logging.error(
            f"Error in POST /v1/auth/salesperson/complete-profile endpoint: {error}"
        )
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
