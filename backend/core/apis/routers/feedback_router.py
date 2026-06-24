"""API routes for feedback-related operations."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from commons.auth import decodeJWT
from commons.logger import logger
from core.apis.schemas.responses_schemas.feedback_response import FeedbackResponse
from core.controller.feedback_controller import FeedbackController
from core.cruds.training_session_crud import CRUDTrainingSession
from core.cruds.user_crud import CRUDUser
from core.models.user_model import UserRole

feedback_router = APIRouter(prefix="/v1/feedback", tags=["feedback"])
logging = logger(__name__)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/salesperson/verify-otp")


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
        logging.warning(f"Inactive user attempted feedback access: {user.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not active",
        )

    if user.role != UserRole.SALESPERSON:
        logging.warning(f"Non-salesperson attempted feedback access: {user.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only salespeople can access feedback",
        )

    return user


async def _require_salesperson_session_access(
    *,
    training_session_id: str,
    salesperson_id: str,
) -> None:
    """Ensure one salesperson can access only their own feedback data.

    Args:
        training_session_id (str): Training session identifier being accessed.
        salesperson_id (str): Authenticated salesperson user identifier.

    Raises:
        HTTPException: If the session does not exist or belongs to another salesperson.
    """
    training_session = await CRUDTrainingSession().get_by_id(id=training_session_id)
    if training_session is None:
        logging.warning(f"Feedback access requested for unknown session {training_session_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training session not found",
        )

    if training_session.user_id != salesperson_id:
        logging.warning(
            "Salesperson attempted feedback access for another user's session: "
            f"{training_session_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this feedback",
        )


@feedback_router.get(
    "/{training_session_id}",
    status_code=status.HTTP_200_OK,
    response_model=FeedbackResponse,
)
async def get_feedback_detail(
    training_session_id: str,
    token: str = Depends(oauth2_scheme),
) -> FeedbackResponse:
    """Fetch one feedback record for the authenticated salesperson.

    Args:
        training_session_id (str): Training session identifier.
        token (str): OAuth2 bearer token for authentication.

    Returns:
        FeedbackResponse: Feedback detail payload.

    Raises:
        HTTPException: If auth validation or feedback lookup fails.
    """
    try:
        logging.info(f"Calling GET /v1/feedback/{training_session_id} endpoint")
        user = await _require_salesperson(token=token)
        await _require_salesperson_session_access(
            training_session_id=training_session_id,
            salesperson_id=str(user.id),
        )
        response = await FeedbackController().get_feedback_detail(
            training_session_id=training_session_id
        )
        return FeedbackResponse(**response)
    except HTTPException as httperror:
        logging.error(
            f"Error in GET /v1/feedback/{training_session_id} endpoint: {httperror}"
        )
        raise httperror
    except Exception as error:
        logging.error(f"Error in GET /v1/feedback/{training_session_id} endpoint: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@feedback_router.post(
    "/{training_session_id}/generate",
    status_code=status.HTTP_200_OK,
    response_model=FeedbackResponse,
)
async def generate_feedback(
    training_session_id: str,
    token: str = Depends(oauth2_scheme),
) -> FeedbackResponse:
    """Generate and persist feedback for one training session.

    Args:
        training_session_id (str): Training session identifier.
        token (str): OAuth2 bearer token for authentication.

    Returns:
        FeedbackResponse: Generated feedback payload.

    Raises:
        HTTPException: If auth validation or feedback generation fails.
    """
    try:
        logging.info(f"Calling POST /v1/feedback/{training_session_id}/generate endpoint")
        user = await _require_salesperson(token=token)
        await _require_salesperson_session_access(
            training_session_id=training_session_id,
            salesperson_id=str(user.id),
        )
        response = await FeedbackController().generate_feedback(
            training_session_id=training_session_id
        )
        return FeedbackResponse(**response)
    except HTTPException as httperror:
        logging.error(
            f"Error in POST /v1/feedback/{training_session_id}/generate endpoint: {httperror}"
        )
        raise httperror
    except Exception as error:
        logging.error(
            f"Error in POST /v1/feedback/{training_session_id}/generate endpoint: {error}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )
