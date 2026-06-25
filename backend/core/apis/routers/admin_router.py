"""API routes for admin dashboard management operations."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordBearer

from commons.auth import decodeJWT
from commons.logger import logger
from core.apis.schemas.requests_schemas.admin_request import (
    SalespersonStatusUpdateRequest,
)
from core.apis.schemas.responses_schemas.admin_response import (
    AdminActionResponse,
    AdminSalespersonListResponse,
    AdminSalespersonResponse,
)
from core.apis.schemas.responses_schemas.conversation_response import (
    ConversationListResponse,
)
from core.apis.schemas.responses_schemas.feedback_response import FeedbackListResponse
from core.apis.schemas.responses_schemas.scenario_response import ScenarioListResponse
from core.controller.admin_controller import AdminController
from core.cruds.user_crud import CRUDUser
from core.models.user_model import UserRole

admin_router = APIRouter(prefix="/v1/admin", tags=["admin"])
logging = logger(__name__)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/v1/auth/verify-otp")


async def _require_admin(token: str):
    """Decode a bearer token and ensure it belongs to an active admin.

    Args:
        token (str): OAuth2 bearer token.

    Returns:
        User: Authenticated active admin user model.

    Raises:
        HTTPException: If the token is invalid or the user is not an active admin.
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
        logging.warning(f"Inactive user attempted admin dashboard access: {user.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User is not active",
        )

    if user.role != UserRole.ADMIN:
        logging.warning(f"Non-admin attempted admin dashboard access: {user.email}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can access admin dashboard routes",
        )

    return user


@admin_router.get(
    "/agents",
    status_code=status.HTTP_200_OK,
    response_model=ScenarioListResponse,
)
async def list_admin_agents(
    active_only: bool = Query(default=True),
    token: str = Depends(oauth2_scheme),
) -> ScenarioListResponse:
    """List training personas available to the admin dashboard.

    Args:
        active_only (bool): Whether only active personas should be returned.
        token (str): OAuth2 bearer token for authentication.

    Returns:
        ScenarioListResponse: Available training personas.

    Raises:
        HTTPException: If auth validation or scenario loading fails.
    """
    try:
        logging.info("Calling GET /v1/admin/agents endpoint")
        await _require_admin(token=token)
        response = await AdminController().list_agents(active_only=active_only)
        return ScenarioListResponse(**response)
    except HTTPException as httperror:
        logging.error(f"Error in GET /v1/admin/agents endpoint: {httperror}")
        raise httperror
    except Exception as error:
        logging.error(f"Error in GET /v1/admin/agents endpoint: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@admin_router.get(
    "/salespeople",
    status_code=status.HTTP_200_OK,
    response_model=AdminSalespersonListResponse,
)
async def list_salespeople(
    token: str = Depends(oauth2_scheme),
) -> AdminSalespersonListResponse:
    """List salesperson records for the admin dashboard.

    Args:
        token (str): OAuth2 bearer token for authentication.

    Returns:
        AdminSalespersonListResponse: Salesperson records for admin management.

    Raises:
        HTTPException: If auth validation or listing fails.
    """
    try:
        logging.info("Calling GET /v1/admin/salespeople endpoint")
        await _require_admin(token=token)
        response = await AdminController().list_salespeople()
        return AdminSalespersonListResponse(**response)
    except HTTPException as httperror:
        logging.error(f"Error in GET /v1/admin/salespeople endpoint: {httperror}")
        raise httperror
    except Exception as error:
        logging.error(f"Error in GET /v1/admin/salespeople endpoint: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@admin_router.patch(
    "/salespeople/{salesperson_id}/status",
    status_code=status.HTTP_200_OK,
    response_model=AdminSalespersonResponse,
)
async def update_salesperson_status(
    salesperson_id: str,
    request: SalespersonStatusUpdateRequest,
    token: str = Depends(oauth2_scheme),
) -> AdminSalespersonResponse:
    """Update salesperson activation status from the admin dashboard.

    Args:
        salesperson_id (str): Salesperson user identifier.
        request (SalespersonStatusUpdateRequest): Desired activation state.
        token (str): OAuth2 bearer token for authentication.

    Returns:
        AdminSalespersonResponse: Updated salesperson record.

    Raises:
        HTTPException: If auth validation or update fails.
    """
    try:
        logging.info(
            f"Calling PATCH /v1/admin/salespeople/{salesperson_id}/status endpoint"
        )
        await _require_admin(token=token)
        response = await AdminController().update_salesperson_status(
            salesperson_id=salesperson_id,
            is_active=request.is_active,
        )
        return AdminSalespersonResponse(**response)
    except HTTPException as httperror:
        logging.error(
            f"Error in PATCH /v1/admin/salespeople/{salesperson_id}/status endpoint: {httperror}"
        )
        raise httperror
    except Exception as error:
        logging.error(
            f"Error in PATCH /v1/admin/salespeople/{salesperson_id}/status endpoint: {error}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@admin_router.get(
    "/salespeople/{salesperson_id}/conversations",
    status_code=status.HTTP_200_OK,
    response_model=ConversationListResponse,
)
async def list_salesperson_conversations(
    salesperson_id: str,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    token: str = Depends(oauth2_scheme),
) -> ConversationListResponse:
    """List conversation history for one salesperson as an admin.

    Args:
        salesperson_id (str): Salesperson user identifier.
        page (int): Page number.
        page_size (int): Maximum items per page.
        token (str): OAuth2 bearer token for authentication.

    Returns:
        ConversationListResponse: Paginated conversation history payload.

    Raises:
        HTTPException: If auth validation or listing fails.
    """
    try:
        logging.info(
            f"Calling GET /v1/admin/salespeople/{salesperson_id}/conversations endpoint"
        )
        await _require_admin(token=token)
        response = await AdminController().list_salesperson_conversations(
            salesperson_id=salesperson_id,
            page=page,
            page_size=page_size,
        )
        return ConversationListResponse(**response)
    except HTTPException as httperror:
        logging.error(
            f"Error in GET /v1/admin/salespeople/{salesperson_id}/conversations endpoint: {httperror}"
        )
        raise httperror
    except Exception as error:
        logging.error(
            f"Error in GET /v1/admin/salespeople/{salesperson_id}/conversations endpoint: {error}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@admin_router.get(
    "/salespeople/{salesperson_id}/feedback",
    status_code=status.HTTP_200_OK,
    response_model=FeedbackListResponse,
)
async def list_salesperson_feedback(
    salesperson_id: str,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    token: str = Depends(oauth2_scheme),
) -> FeedbackListResponse:
    """List feedback history for one salesperson as an admin.

    Args:
        salesperson_id (str): Salesperson user identifier.
        page (int): Page number.
        page_size (int): Maximum items per page.
        token (str): OAuth2 bearer token for authentication.

    Returns:
        FeedbackListResponse: Paginated feedback history payload.

    Raises:
        HTTPException: If auth validation or listing fails.
    """
    try:
        logging.info(
            f"Calling GET /v1/admin/salespeople/{salesperson_id}/feedback endpoint"
        )
        await _require_admin(token=token)
        response = await AdminController().list_salesperson_feedback(
            salesperson_id=salesperson_id,
            page=page,
            page_size=page_size,
        )
        return FeedbackListResponse(**response)
    except HTTPException as httperror:
        logging.error(
            f"Error in GET /v1/admin/salespeople/{salesperson_id}/feedback endpoint: {httperror}"
        )
        raise httperror
    except Exception as error:
        logging.error(
            f"Error in GET /v1/admin/salespeople/{salesperson_id}/feedback endpoint: {error}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@admin_router.delete(
    "/salespeople/{salesperson_id}",
    status_code=status.HTTP_200_OK,
    response_model=AdminActionResponse,
)
async def delete_salesperson(
    salesperson_id: str,
    token: str = Depends(oauth2_scheme),
) -> AdminActionResponse:
    """Delete one salesperson record from the admin dashboard.

    Args:
        salesperson_id (str): Salesperson user identifier.
        token (str): OAuth2 bearer token for authentication.

    Returns:
        AdminActionResponse: Delete result payload.

    Raises:
        HTTPException: If auth validation or delete fails.
    """
    try:
        logging.info(f"Calling DELETE /v1/admin/salespeople/{salesperson_id} endpoint")
        await _require_admin(token=token)
        response = await AdminController().delete_salesperson(
            salesperson_id=salesperson_id
        )
        return AdminActionResponse(**response)
    except HTTPException as httperror:
        logging.error(
            f"Error in DELETE /v1/admin/salespeople/{salesperson_id} endpoint: {httperror}"
        )
        raise httperror
    except Exception as error:
        logging.error(
            f"Error in DELETE /v1/admin/salespeople/{salesperson_id} endpoint: {error}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )
