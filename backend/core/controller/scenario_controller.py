"""Controller logic for scenario-related workflows."""

from fastapi import HTTPException, status

from commons.logger import logger
from core.cruds.scenario_crud import CRUDScenario
from core.models.scenario_model import Scenario

logging = logger(__name__)


class ScenarioController:
    """Business orchestration for scenario workflows."""

    def __init__(self) -> None:
        """Initialize CRUD dependencies for scenario workflows."""
        self.crud_scenario = CRUDScenario()

    @staticmethod
    def _serialize_scenario(scenario: Scenario) -> dict:
        """Convert a scenario model into the response shape.

        Args:
            scenario (Scenario): Persisted scenario model instance.

        Returns:
            dict: Scenario response payload.
        """
        return {
            "id": str(scenario.id),
            "key": scenario.key,
            "title": scenario.title,
            "description": scenario.description,
            "agent_id": scenario.agent_id,
            "is_active": scenario.is_active,
            "sort_order": scenario.sort_order,
        }

    async def list_scenarios(self, *, active_only: bool = True) -> dict:
        """List scenarios available to the frontend.

        Args:
            active_only (bool): Whether only active scenarios should be returned.

        Returns:
            dict: Scenario list response payload.

        Raises:
            HTTPException: If the scenario read fails unexpectedly.
        """
        try:
            logging.info("Executing ScenarioController.list_scenarios")
            scenarios = await self.crud_scenario.list_active()
            items = [self._serialize_scenario(scenario) for scenario in scenarios]

            if not active_only:
                items = sorted(items, key=lambda item: item["sort_order"])
                return {"items": items}

            active_items = [item for item in items if item["is_active"]]
            active_items.sort(key=lambda item: item["sort_order"])
            return {"items": active_items}
        except Exception as error:
            logging.error(f"Error in ScenarioController.list_scenarios: {error}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal Server Error",
            )
