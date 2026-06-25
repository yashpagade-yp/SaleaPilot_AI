"""Controller logic for admin dashboard management workflows."""

from datetime import datetime, timezone

from fastapi import HTTPException, status

from commons.logger import logger
from core.controller.conversation_controller import ConversationController
from core.controller.feedback_controller import FeedbackController
from core.controller.scenario_controller import ScenarioController
from core.cruds.feedback_crud import CRUDFeedback
from core.cruds.invitation_crud import CRUDInvitation
from core.cruds.training_session_crud import CRUDTrainingSession
from core.cruds.user_crud import CRUDUser
from core.database.database import get_utc_now
from core.models.invitation_model import InvitationStatus
from core.models.user_model import User, UserRole

logging = logger(__name__)


class AdminController:
    """Business orchestration for admin dashboard workflows."""

    def __init__(self) -> None:
        """Initialize CRUD and controller dependencies for admin workflows."""
        self.crud_user = CRUDUser()
        self.crud_invitation = CRUDInvitation()
        self.crud_training_session = CRUDTrainingSession()
        self.crud_feedback = CRUDFeedback()
        self.conversation_controller = ConversationController()
        self.feedback_controller = FeedbackController()
        self.scenario_controller = ScenarioController()

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

    @staticmethod
    def _resolve_dashboard_status(*, user: User, latest_invitation) -> str:
        """Resolve the admin dashboard status for one salesperson.

        Args:
            user (User): Salesperson user model.
            latest_invitation: Latest invitation model or None.

        Returns:
            str: Dashboard status label.
        """
        if user.is_active:
            return "ACTIVE"

        if (
            latest_invitation is not None
            and latest_invitation.status == InvitationStatus.PENDING
            and AdminController._as_utc(latest_invitation.expires_at) > get_utc_now()
        ):
            return "INVITED"

        return "INACTIVE"

    async def _require_salesperson(self, *, salesperson_id: str) -> User:
        """Load one salesperson user or raise a domain-safe error.

        Args:
            salesperson_id (str): Salesperson user identifier.

        Returns:
            User: Matching salesperson user model.

        Raises:
            HTTPException: If the user does not exist or is not a salesperson.
        """
        user = await self.crud_user.get_by_id(id=salesperson_id)
        if user is None:
            logging.warning(f"Admin requested unknown salesperson {salesperson_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Salesperson not found",
            )

        if user.role != UserRole.SALESPERSON:
            logging.warning(f"Admin requested non-salesperson user {salesperson_id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Requested user is not a salesperson",
            )

        return user

    async def list_salespeople(self) -> dict:
        """List salesperson records for the admin dashboard.

        Returns:
            dict: Admin salesperson list payload.

        Raises:
            HTTPException: If listing users fails unexpectedly.
        """
        try:
            logging.info("Executing AdminController.list_salespeople")
            salespeople = await self.crud_user.list_by_role(role=UserRole.SALESPERSON)
            items: list[dict] = []

            for user in salespeople:
                invitations = await self.crud_invitation.list_by_email(email=user.email)
                latest_invitation = (
                    max(invitations, key=lambda invitation: invitation.created_at)
                    if invitations
                    else None
                )
                items.append(
                    {
                        "id": str(user.id),
                        "first_name": user.first_name,
                        "last_name": user.last_name,
                        "email": user.email,
                        "phone_number": user.phone_number,
                        "role": user.role,
                        "is_active": user.is_active,
                        "status": self._resolve_dashboard_status(
                            user=user,
                            latest_invitation=latest_invitation,
                        ),
                        "last_login_at": user.last_login_at,
                        "updated_at": user.updated_at,
                        "latest_invitation_sent_at": (
                            latest_invitation.created_at if latest_invitation else None
                        ),
                        "latest_invitation_expires_at": (
                            latest_invitation.expires_at if latest_invitation else None
                        ),
                        "latest_invitation_status": (
                            latest_invitation.status if latest_invitation else None
                        ),
                    }
                )

            items.sort(
                key=lambda item: (
                    item["status"] != "INVITED",
                    item["status"] != "ACTIVE",
                    item["updated_at"],
                )
            )
            items.reverse()
            return {"items": items}
        except HTTPException:
            raise
        except Exception as error:
            logging.error(f"Error in AdminController.list_salespeople: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )

    async def update_salesperson_status(
        self,
        *,
        salesperson_id: str,
        is_active: bool,
    ) -> dict:
        """Update salesperson activation state from the admin dashboard.

        Args:
            salesperson_id (str): Salesperson user identifier.
            is_active (bool): Desired activation state.

        Returns:
            dict: Updated salesperson payload.

        Raises:
            HTTPException: If the salesperson is not found or update fails.
        """
        try:
            logging.info("Executing AdminController.update_salesperson_status")
            user = await self._require_salesperson(salesperson_id=salesperson_id)
            updated_user = await self.crud_user.update(
                id=str(user.id),
                obj_in={
                    "is_active": is_active,
                    "otp": None,
                },
            )
            if updated_user is None:
                logging.error(
                    f"Failed to update salesperson status for {salesperson_id}"
                )
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to update salesperson status",
                )

            if not is_active:
                invitations = await self.crud_invitation.list_by_email(email=user.email)
                for invitation in invitations:
                    if (
                        invitation.status == InvitationStatus.PENDING
                        and self._as_utc(invitation.expires_at) <= get_utc_now()
                    ):
                        await self.crud_invitation.update(
                            id=str(invitation.id),
                            obj_in={"status": InvitationStatus.EXPIRED},
                        )

            latest_invitation = None
            invitations = await self.crud_invitation.list_by_email(email=updated_user.email)
            if invitations:
                latest_invitation = max(
                    invitations,
                    key=lambda invitation: invitation.created_at,
                )

            return {
                "id": str(updated_user.id),
                "first_name": updated_user.first_name,
                "last_name": updated_user.last_name,
                "email": updated_user.email,
                "phone_number": updated_user.phone_number,
                "role": updated_user.role,
                "is_active": updated_user.is_active,
                "status": self._resolve_dashboard_status(
                    user=updated_user,
                    latest_invitation=latest_invitation,
                ),
                "last_login_at": updated_user.last_login_at,
                "updated_at": updated_user.updated_at,
                "latest_invitation_sent_at": (
                    latest_invitation.created_at if latest_invitation else None
                ),
                "latest_invitation_expires_at": (
                    latest_invitation.expires_at if latest_invitation else None
                ),
                "latest_invitation_status": (
                    latest_invitation.status if latest_invitation else None
                ),
            }
        except HTTPException:
            raise
        except Exception as error:
            logging.error(f"Error in AdminController.update_salesperson_status: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )

    async def list_salesperson_conversations(
        self,
        *,
        salesperson_id: str,
        page: int,
        page_size: int,
    ) -> dict:
        """List conversation history for one salesperson as an admin.

        Args:
            salesperson_id (str): Salesperson user identifier.
            page (int): Page number.
            page_size (int): Maximum items per page.

        Returns:
            dict: Paginated conversation history payload.
        """
        try:
            logging.info("Executing AdminController.list_salesperson_conversations")
            await self._require_salesperson(salesperson_id=salesperson_id)
            training_sessions = await self.crud_training_session.list_by_user_id(
                user_id=salesperson_id
            )
            training_session_ids = [str(session.id) for session in training_sessions]
            return await self.conversation_controller.list_conversation_history(
                training_session_ids=training_session_ids,
                page=page,
                page_size=page_size,
            )
        except HTTPException:
            raise
        except Exception as error:
            logging.error(
                f"Error in AdminController.list_salesperson_conversations: {error}"
            )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )

    async def list_salesperson_feedback(
        self,
        *,
        salesperson_id: str,
        page: int,
        page_size: int,
    ) -> dict:
        """List feedback history for one salesperson as an admin.

        Args:
            salesperson_id (str): Salesperson user identifier.
            page (int): Page number.
            page_size (int): Maximum items per page.

        Returns:
            dict: Paginated feedback history payload.
        """
        try:
            logging.info("Executing AdminController.list_salesperson_feedback")
            await self._require_salesperson(salesperson_id=salesperson_id)
            feedback_items = await self.crud_feedback.list_by_user_id(user_id=salesperson_id)
            serialized_items = [
                self.feedback_controller._serialize_feedback(item)
                for item in feedback_items
            ]
            serialized_items.sort(
                key=lambda item: item["created_at"],
                reverse=True,
            )
            total = len(serialized_items)
            start_index = (page - 1) * page_size
            end_index = start_index + page_size
            return {
                "items": serialized_items[start_index:end_index],
                "page": page,
                "page_size": page_size,
                "total": total,
            }
        except HTTPException:
            raise
        except Exception as error:
            logging.error(f"Error in AdminController.list_salesperson_feedback: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )

    async def list_agents(self, *, active_only: bool) -> dict:
        """List training personas for the admin dashboard.

        Args:
            active_only (bool): Whether only active personas should be returned.

        Returns:
            dict: Scenario list payload for the `Agents` section.
        """
        try:
            logging.info("Executing AdminController.list_agents")
            return await self.scenario_controller.list_scenarios(active_only=active_only)
        except HTTPException:
            raise
        except Exception as error:
            logging.error(f"Error in AdminController.list_agents: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )

    async def delete_salesperson(self, *, salesperson_id: str) -> dict:
        """Delete one salesperson when no practice history exists.

        Args:
            salesperson_id (str): Salesperson user identifier.

        Returns:
            dict: Human-readable delete result.

        Raises:
            HTTPException: If the salesperson has practice history or delete fails.
        """
        try:
            logging.info("Executing AdminController.delete_salesperson")
            user = await self._require_salesperson(salesperson_id=salesperson_id)
            training_sessions = await self.crud_training_session.list_by_user_id(
                user_id=str(user.id)
            )
            if training_sessions:
                logging.warning(
                    f"Admin attempted to delete salesperson with practice history: {salesperson_id}"
                )
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Cannot delete a salesperson with existing practice history",
                )

            await self.crud_invitation.delete_by_email(email=user.email)
            deleted = await self.crud_user.delete(id=str(user.id))
            if not deleted:
                logging.error(f"Failed to delete salesperson {salesperson_id}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to delete salesperson",
                )

            return {
                "message": f"Salesperson {user.email} deleted successfully",
            }
        except HTTPException:
            raise
        except Exception as error:
            logging.error(f"Error in AdminController.delete_salesperson: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )
