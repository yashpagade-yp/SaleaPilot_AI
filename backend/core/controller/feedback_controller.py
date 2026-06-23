"""Controller logic for feedback-related workflows."""

from fastapi import HTTPException, status

from commons.logger import logger
from core.cruds.feedback_crud import CRUDFeedback
from core.models.feedback_model import Feedback

logging = logger(__name__)


class FeedbackController:
    """Business orchestration for feedback workflows."""

    def __init__(self) -> None:
        """Initialize CRUD dependencies for feedback workflows."""
        self.crud_feedback = CRUDFeedback()

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
