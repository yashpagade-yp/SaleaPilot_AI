"""Controller logic for feedback-related workflows."""

from fastapi import HTTPException, status

from commons.logger import logger
from core.controller.conversation_controller import ConversationController
from core.cruds.conversation_crud import CRUDConversation
from core.cruds.feedback_crud import CRUDFeedback
from core.cruds.scenario_crud import CRUDScenario
from core.cruds.training_session_crud import CRUDTrainingSession
from core.models.feedback_model import Feedback
from core.services.feedback_service import FeedbackGenerationService

logging = logger(__name__)


class FeedbackController:
    """Business orchestration for feedback workflows."""

    def __init__(self) -> None:
        """Initialize CRUD dependencies for feedback workflows."""
        self.crud_feedback = CRUDFeedback()
        self.crud_training_session = CRUDTrainingSession()
        self.crud_scenario = CRUDScenario()
        self.crud_conversation = CRUDConversation()
        self.conversation_controller = ConversationController()
        self.feedback_service = FeedbackGenerationService()

    @staticmethod
    def _serialize_feedback(feedback: Feedback) -> dict:
        """Convert a feedback model into the response shape.

        Args:
            feedback (Feedback): Persisted feedback model.

        Returns:
            dict: Feedback response payload.
        """
        return {
            "id": str(feedback.id),
            "training_session_id": feedback.training_session_id,
            "user_id": feedback.user_id,
            "scenario_id": feedback.scenario_id,
            "summary": feedback.summary,
            "strengths": feedback.strengths,
            "improvement_areas": feedback.improvement_areas,
            "objection_handling_score": feedback.objection_handling_score,
            "confidence_score": feedback.confidence_score,
            "clarity_score": feedback.clarity_score,
            "rapport_score": feedback.rapport_score,
            "closing_score": feedback.closing_score,
            "recommendations": feedback.recommendations,
            "raw_feedback_payload": feedback.raw_feedback_payload,
            "created_at": feedback.created_at,
        }

    async def get_feedback_detail(self, *, training_session_id: str) -> dict:
        """Fetch one feedback record by training session identifier.

        Args:
            training_session_id (str): Training session identifier.

        Returns:
            dict: Serialized feedback response payload.

        Raises:
            HTTPException: If the feedback record is not found.
        """
        try:
            logging.info("Executing FeedbackController.get_feedback_detail")
            feedback = await self.crud_feedback.get_by_training_session_id(
                training_session_id=training_session_id
            )
            if feedback is None:
                logging.warning(
                    f"No feedback found for training session {training_session_id}"
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Feedback not found",
                )

            return self._serialize_feedback(feedback)
        except HTTPException:
            raise
        except Exception as error:
            logging.error(f"Error in FeedbackController.get_feedback_detail: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )

    async def generate_feedback(self, *, training_session_id: str) -> dict:
        """Generate and persist feedback for one training session.

        Args:
            training_session_id (str): Training session identifier.

        Returns:
            dict: Serialized generated feedback payload.

        Raises:
            HTTPException: If the required session or conversation data is missing.
        """
        try:
            logging.info("Executing FeedbackController.generate_feedback")
            training_session = await self.crud_training_session.get_by_id(
                id=training_session_id
            )
            if training_session is None:
                logging.warning(
                    f"Feedback generation requested for unknown session {training_session_id}"
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Training session not found",
                )

            scenario = await self.crud_scenario.get_by_id(id=training_session.scenario_id)
            if scenario is None:
                logging.warning(
                    f"Feedback generation requested for missing scenario {training_session.scenario_id}"
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Scenario not found",
                )

            conversation_record = await self.crud_conversation.get_by_training_session_id(
                training_session_id=training_session_id
            )
            if conversation_record is None:
                logging.warning(
                    f"Feedback generation requested for missing conversation {training_session_id}"
                )
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Conversation not found",
                )

            transcript = conversation_record.transcript or ""
            analysis = conversation_record.analysis or {}
            if not transcript and not analysis:
                conversation = await self.conversation_controller.sync_conversation(
                    training_session_id=training_session_id
                )
                transcript = conversation.get("transcript") or ""
                analysis = conversation.get("analysis") or {}

            if not transcript and not analysis:
                logging.warning(
                    f"Feedback generation requested before transcript/analysis was ready: {training_session_id}"
                )
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Conversation transcript or analysis is not available yet",
                )

            feedback_payload = self.feedback_service.generate_feedback(
                transcript=transcript,
                scenario_title=scenario.title,
                conversation_analysis=analysis,
            )
            feedback_data = {
                "training_session_id": training_session_id,
                "user_id": training_session.user_id,
                "scenario_id": training_session.scenario_id,
                **feedback_payload,
            }

            existing_feedback = await self.crud_feedback.get_by_training_session_id(
                training_session_id=training_session_id
            )
            if existing_feedback is None:
                feedback = await self.crud_feedback.create(obj_in=feedback_data)
            else:
                feedback = await self.crud_feedback.update(
                    id=str(existing_feedback.id),
                    obj_in=feedback_data,
                )
                if feedback is None:
                    logging.error(
                        f"Failed to update feedback during generation: {training_session_id}"
                    )
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Failed to update feedback",
                    )

            return self._serialize_feedback(feedback)
        except HTTPException:
            raise
        except Exception as error:
            logging.error(f"Error in FeedbackController.generate_feedback: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )
