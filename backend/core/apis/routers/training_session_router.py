"""API routes for training-session-related operations."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from commons.auth import decodeJWT
from commons.logger import logger
from core.apis.schemas.requests_schemas.training_session_request import (
    StartTrainingSessionRequest,
)
from core.apis.schemas.responses_schemas.training_session_response import (
    StartTrainingSessionResponse,
    TrainingSessionResponse,
)
from core.controller.training_session_controller import TrainingSessionController
from core.cruds.user_crud import CRUDUser
from core.models.user_model import UserRole

training_session_router = APIRouter(
    prefix="/v1/training-sessions",
    tags=["training-sessions"],
)
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
        logging.warning(
            f"Inactive user attempted training-session access: {user.email}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not active",
        )

    if user.role != UserRole.SALESPERSON:
        logging.warning(f"Non-salesperson attempted training-session access: {user.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only salespeople can access training sessions",
        )

    return user


@training_session_router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=StartTrainingSessionResponse,
)
async def start_training_session(
    request: StartTrainingSessionRequest,
    token: str = Depends(oauth2_scheme),
) -> StartTrainingSessionResponse:
    """Create a training session for the authenticated salesperson.

    Args:
        request (StartTrainingSessionRequest): Training session creation payload.
        token (str): OAuth2 bearer token for authentication.

    Returns:
        StartTrainingSessionResponse: Created session details.

    Raises:
        HTTPException: If auth validation or session creation fails.
    """
    try:
        logging.info("Calling POST /v1/training-sessions endpoint")
        user = await _require_salesperson(token=token)
        response = await TrainingSessionController().start_training_session(
            user_id=str(user.id),
            scenario_key=request.scenario_key,
        )
        return StartTrainingSessionResponse(**response)
    except HTTPException as httperror:
        logging.error(f"Error in POST /v1/training-sessions endpoint: {httperror}")
        raise httperror
    except Exception as error:
        logging.error(f"Error in POST /v1/training-sessions endpoint: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@training_session_router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=list[TrainingSessionResponse],
)
async def list_training_sessions(
    token: str = Depends(oauth2_scheme),
) -> list[TrainingSessionResponse]:
    """List training sessions for the authenticated salesperson.

    Args:
        token (str): OAuth2 bearer token for authentication.

    Returns:
        list[TrainingSessionResponse]: User training sessions.

    Raises:
        HTTPException: If auth validation or session loading fails.
    """
    try:
        logging.info("Calling GET /v1/training-sessions endpoint")
        user = await _require_salesperson(token=token)
        response = await TrainingSessionController().list_user_training_sessions(
            user_id=str(user.id)
        )
        return [TrainingSessionResponse(**item) for item in response]
    except HTTPException as httperror:
        logging.error(f"Error in GET /v1/training-sessions endpoint: {httperror}")
        raise httperror
    except Exception as error:
        logging.error(f"Error in GET /v1/training-sessions endpoint: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )
