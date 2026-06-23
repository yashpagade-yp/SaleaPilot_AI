"""API routes for feedback-related operations."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from commons.auth import decodeJWT
from commons.logger import logger
from core.apis.schemas.responses_schemas.feedback_response import FeedbackResponse
from core.controller.feedback_controller import FeedbackController
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
        await _require_salesperson(token=token)
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
        await _require_salesperson(token=token)
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
