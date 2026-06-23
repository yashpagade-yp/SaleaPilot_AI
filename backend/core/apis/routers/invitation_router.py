"""API routes for invitation-related operations."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from commons.auth import decodeJWT
from commons.logger import logger
from core.apis.schemas.requests_schemas.invitation_request import (
    AcceptInvitationRequest,
    SendInvitationRequest,
)
from core.apis.schemas.responses_schemas.invitation_response import (
    InvitationAcceptResponse,
    InvitationResponse,
)
from core.controller.invitation_controller import InvitationController
from core.cruds.user_crud import CRUDUser
from core.models.user_model import UserRole

invitation_router = APIRouter(prefix="/v1/invitations", tags=["invitations"])
logging = logger(__name__)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/salesperson/login")


async def _get_authenticated_user(token: str):
    """Decode a bearer token and resolve the backing user record.

    Args:
        token (str): OAuth2 bearer token.

    Returns:
        User: Authenticated user model instance.

    Raises:
        HTTPException: If the token is invalid or the user is not active.
    """
    authenticated_user_details = decodeJWT(token=token)
    if not authenticated_user_details:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    user = await CRUDUser().get_by_id(id=authenticated_user_details.get("id", ""))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )

    if not user.is_active:
        logging.warning(f"Inactive user attempted invitation access: {user.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not active",
        )

    return user


@invitation_router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=InvitationResponse,
)
async def send_invitation(
    request: SendInvitationRequest,
    token: str = Depends(oauth2_scheme),
) -> InvitationResponse:
    """Create a salesperson invitation for an authenticated admin.

    Args:
        request (SendInvitationRequest): Invitation creation payload.
        token (str): OAuth2 bearer token for authentication.

    Returns:
        InvitationResponse: Created invitation details.

    Raises:
        HTTPException: If the user is not an active admin or creation fails.
    """
    try:
        logging.info("Calling POST /v1/invitations endpoint")
        user = await _get_authenticated_user(token=token)
        if user.role != UserRole.ADMIN:
            logging.warning(f"Non-admin user attempted invitation create: {user.email}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only admins can send invitations",
            )

        response = await InvitationController().send_invitation(
            email=request.email,
            first_name=request.first_name,
            last_name=request.last_name,
            invited_by=str(user.id),
        )
        return InvitationResponse(**response)
    except HTTPException as httperror:
        logging.error(f"Error in POST /v1/invitations endpoint: {httperror}")
        raise httperror
    except Exception as error:
        logging.error(f"Error in POST /v1/invitations endpoint: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@invitation_router.post(
    "/accept",
    status_code=status.HTTP_200_OK,
    response_model=InvitationAcceptResponse,
)
async def accept_invitation(
    request: AcceptInvitationRequest,
) -> InvitationAcceptResponse:
    """Accept a pending invitation and create a salesperson account.

    Args:
        request (AcceptInvitationRequest): Invitation acceptance payload.

    Returns:
        InvitationAcceptResponse: Account creation acknowledgement payload.

    Raises:
        HTTPException: If the invitation is invalid or acceptance fails.
    """
    try:
        logging.info("Calling POST /v1/invitations/accept endpoint")
        response = await InvitationController().accept_invitation(
            token=request.token,
            first_name=request.first_name,
            last_name=request.last_name,
            password=request.password,
        )
        return InvitationAcceptResponse(**response)
    except HTTPException as httperror:
        logging.error(f"Error in POST /v1/invitations/accept endpoint: {httperror}")
        raise httperror
    except Exception as error:
        logging.error(f"Error in POST /v1/invitations/accept endpoint: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )
