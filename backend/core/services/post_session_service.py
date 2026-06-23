"""Background post-session automation for transcript sync and feedback generation."""

import asyncio
from contextlib import suppress

from commons.logger import logger
from core.controller.conversation_controller import ConversationController
from core.controller.feedback_controller import FeedbackController
from core.cruds.feedback_crud import CRUDFeedback
from core.cruds.training_session_crud import CRUDTrainingSession
from core.models.training_session_model import TrainingSessionStatus

logging = logger(__name__)


class PostSessionAutomationService:
    """Background processor for automatic session sync and feedback generation."""

    def __init__(self) -> None:
        """Initialize dependencies used by the post-session worker."""
        logging.info("Executing PostSessionAutomationService.__init__")
        self.crud_training_session = CRUDTrainingSession()
        self.crud_feedback = CRUDFeedback()
        self.conversation_controller = ConversationController()
        self.feedback_controller = FeedbackController()
        self.poll_interval_seconds = 20
        self._worker_task: asyncio.Task | None = None
        self._is_processing = False

    async def start(self) -> None:
        """Start the background automation worker if it is not already running."""
        logging.info("Executing PostSessionAutomationService.start")
        if self._worker_task is None or self._worker_task.done():
            self._worker_task = asyncio.create_task(self._worker_loop())

    async def stop(self) -> None:
        """Stop the background automation worker gracefully."""
        logging.info("Executing PostSessionAutomationService.stop")
        if self._worker_task is None:
            return

        self._worker_task.cancel()
        with suppress(asyncio.CancelledError):
            await self._worker_task
        self._worker_task = None

    async def run_once(self) -> None:
        """Execute one automation pass across active training sessions."""
        if self._is_processing:
            logging.info("Skipping post-session run because processing is already active")
            return

        self._is_processing = True
        try:
            logging.info("Executing PostSessionAutomationService.run_once")
            in_progress_sessions = await self.crud_training_session.list_by_status(
                status=TrainingSessionStatus.IN_PROGRESS
            )

            for session in in_progress_sessions:
                if not session.conversation_id:
                    continue

                try:
                    conversation = await self.conversation_controller.sync_conversation(
                        training_session_id=str(session.id)
                    )
                    if conversation.get("conversation_status") != "COMPLETED":
                        continue

                    existing_feedback = await self.crud_feedback.get_by_training_session_id(
                        training_session_id=str(session.id)
                    )
                    if existing_feedback is not None:
                        continue

                    await self.feedback_controller.generate_feedback(
                        training_session_id=str(session.id)
                    )
                    logging.info(
                        "Automatic feedback generated successfully for training session "
                        f"{session.id}"
                    )
                except Exception as error:
                    logging.error(
                        "Error while processing post-session automation for training session "
                        f"{session.id}: {error}"
                    )
        finally:
            self._is_processing = False

    async def _worker_loop(self) -> None:
        """Run the post-session automation loop until shutdown."""
        logging.info("Executing PostSessionAutomationService._worker_loop")
        try:
            while True:
                await self.run_once()
                await asyncio.sleep(self.poll_interval_seconds)
        except asyncio.CancelledError:
            logging.info("Post-session automation worker cancelled")
            raise
