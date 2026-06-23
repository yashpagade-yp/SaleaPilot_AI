"""API routes for scenario-related operations."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordBearer

from commons.auth import decodeJWT
from commons.logger import logger
from core.apis.schemas.responses_schemas.scenario_response import ScenarioListResponse
from core.controller.scenario_controller import ScenarioController
from core.cruds.user_crud import CRUDUser

scenario_router = APIRouter(prefix="/v1/scenarios", tags=["scenarios"])
logging = logger(__name__)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/salesperson/verify-otp")


async def _require_active_user(token: str):
    """Decode a bearer token and ensure the user exists and is active.

    Args:
        token (str): OAuth2 bearer token.

    Returns:
        User: Authenticated active user model.

    Raises:
        HTTPException: If the token is invalid or user access is blocked.
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
        logging.warning(f"Inactive user attempted scenario access: {user.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not active",
        )

    return user


@scenario_router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=ScenarioListResponse,
)
async def list_scenarios(
    active_only: bool = Query(default=True),
    token: str = Depends(oauth2_scheme),
) -> ScenarioListResponse:
    """List training scenarios available to the authenticated user.

    Args:
        active_only (bool): Whether only active scenarios should be returned.
        token (str): OAuth2 bearer token for authentication.

    Returns:
        ScenarioListResponse: Available training scenarios.

    Raises:
        HTTPException: If auth validation or scenario loading fails.
    """
    try:
        logging.info("Calling GET /v1/scenarios endpoint")
        await _require_active_user(token=token)
        response = await ScenarioController().list_scenarios(active_only=active_only)
        return ScenarioListResponse(**response)
    except HTTPException as httperror:
        logging.error(f"Error in GET /v1/scenarios endpoint: {httperror}")
        raise httperror
    except Exception as error:
        logging.error(f"Error in GET /v1/scenarios endpoint: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )
