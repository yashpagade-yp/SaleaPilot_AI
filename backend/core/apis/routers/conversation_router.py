"""API routes for conversation-related operations."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordBearer

from commons.auth import decodeJWT
from commons.logger import logger
from core.apis.schemas.responses_schemas.conversation_response import (
    ConversationListResponse,
    ConversationResponse,
)
from core.controller.conversation_controller import ConversationController
from core.controller.training_session_controller import TrainingSessionController
from core.cruds.user_crud import CRUDUser
from core.models.user_model import UserRole

conversation_router = APIRouter(prefix="/v1/conversations", tags=["conversations"])
logging = logger(__name__)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/salesperson/login")


async def _require_salesperson(token: str):
    """Decode a bearer token and ensure it belongs to an active salesperson.

    Args:
        token (str): OAuth2 bearer token.

    Returns:
        User: Authenticated active salesperson user model.

    Raises:
        HTTPException: If the token is invalid or the user is not an active salesperson.
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
        logging.warning(f"Inactive user attempted conversation access: {user.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not active",
        )

    if user.role != UserRole.SALESPERSON:
        logging.warning(f"Non-salesperson attempted conversation access: {user.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only salespeople can access conversations",
        )

    return user


@conversation_router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=ConversationListResponse,
)
async def list_conversation_history(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    token: str = Depends(oauth2_scheme),
) -> ConversationListResponse:
    """List conversation history for the authenticated salesperson.

    Args:
        page (int): Page number for paginated history.
        page_size (int): Maximum items per page.
        token (str): OAuth2 bearer token for authentication.

    Returns:
        ConversationListResponse: Paginated conversation history payload.

    Raises:
        HTTPException: If auth validation or conversation loading fails.
    """
    try:
        logging.info("Calling GET /v1/conversations endpoint")
        user = await _require_salesperson(token=token)
        training_sessions = await TrainingSessionController().list_user_training_sessions(
            user_id=str(user.id)
        )
        training_session_ids = [item["id"] for item in training_sessions]
        response = await ConversationController().list_conversation_history(
            training_session_ids=training_session_ids,
            page=page,
            page_size=page_size,
        )
        return ConversationListResponse(**response)
    except HTTPException as httperror:
        logging.error(f"Error in GET /v1/conversations endpoint: {httperror}")
        raise httperror
    except Exception as error:
        logging.error(f"Error in GET /v1/conversations endpoint: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@conversation_router.get(
    "/{training_session_id}",
    status_code=status.HTTP_200_OK,
    response_model=ConversationResponse,
)
async def get_conversation_detail(
    training_session_id: str,
    token: str = Depends(oauth2_scheme),
) -> ConversationResponse:
    """Fetch one conversation record for the authenticated salesperson.

    Args:
        training_session_id (str): Training session identifier.
        token (str): OAuth2 bearer token for authentication.

    Returns:
        ConversationResponse: Conversation detail payload.

    Raises:
        HTTPException: If auth validation or conversation lookup fails.
    """
    try:
        logging.info(f"Calling GET /v1/conversations/{training_session_id} endpoint")
        await _require_salesperson(token=token)
        response = await ConversationController().get_conversation_detail(
            training_session_id=training_session_id
        )
        return ConversationResponse(**response)
    except HTTPException as httperror:
        logging.error(
            f"Error in GET /v1/conversations/{training_session_id} endpoint: {httperror}"
        )
        raise httperror
    except Exception as error:
        logging.error(
            f"Error in GET /v1/conversations/{training_session_id} endpoint: {error}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@conversation_router.post(
    "/{training_session_id}/sync",
    status_code=status.HTTP_200_OK,
    response_model=ConversationResponse,
)
async def sync_conversation(
    training_session_id: str,
    token: str = Depends(oauth2_scheme),
) -> ConversationResponse:
    """Sync one conversation from Eigi into local persistence.

    Args:
        training_session_id (str): Training session identifier.
        token (str): OAuth2 bearer token for authentication.

    Returns:
        ConversationResponse: Synced conversation payload.

    Raises:
        HTTPException: If auth validation or sync fails.
    """
    try:
        logging.info(
            f"Calling POST /v1/conversations/{training_session_id}/sync endpoint"
        )
        await _require_salesperson(token=token)
        response = await ConversationController().sync_conversation(
            training_session_id=training_session_id
        )
        return ConversationResponse(**response)
    except HTTPException as httperror:
        logging.error(
            "Error in POST /v1/conversations/"
            f"{training_session_id}/sync endpoint: {httperror}"
        )
        raise httperror
    except Exception as error:
        logging.error(
            "Error in POST /v1/conversations/"
            f"{training_session_id}/sync endpoint: {error}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )
