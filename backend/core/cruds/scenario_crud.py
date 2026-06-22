"""CRUD operations for scenario records."""

from fastapi import HTTPException, status

from commons.logger import logger
from core.database.database import get_engine, get_utc_now, parse_object_id
from core.models.scenario_model import Scenario, ScenarioKey

logging = logger(__name__)


class CRUDScenario:
    """Database access layer for scenario records."""

    async def create(self, *, obj_in: dict) -> Scenario:
        """Create a new scenario record.

        Args:
            obj_in (dict): Scenario creation payload.

        Returns:
            Scenario: Created scenario model instance.

        Raises:
            Exception: If the database write fails.
        """
        try:
            logging.info("Executing CRUDScenario.create")
            scenario = Scenario(**obj_in)
            await get_engine().save(scenario)
            return scenario
        except Exception as error:
            logging.error(f"Error in CRUDScenario.create: {error}")
            raise error

    async def get_by_id(self, *, id: str) -> Scenario | None:
        """Read a scenario record by unique identifier.

        Args:
            id (str): Scenario identifier.

        Returns:
            Scenario | None: Matching scenario model or None when not found.

        Raises:
            HTTPException 400: If the identifier is invalid.
            Exception: If the database read fails.
        """
        try:
            logging.info("Executing CRUDScenario.get_by_id")
            return await get_engine().find_one(
                Scenario,
                Scenario.id == parse_object_id(id),
            )
        except ValueError as error:
            logging.warning(f"Invalid scenario id received: {id}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(error),
            ) from error
        except Exception as error:
            logging.error(f"Error in CRUDScenario.get_by_id: {error}")
            raise error

    async def get_by_key(self, *, key: ScenarioKey) -> Scenario | None:
        """Read a scenario record by fixed scenario key.

        Args:
            key (ScenarioKey): Scenario key to match.

        Returns:
            Scenario | None: Matching scenario model or None when not found.

        Raises:
            Exception: If the database read fails.
        """
        try:
            logging.info("Executing CRUDScenario.get_by_key")
            return await get_engine().find_one(Scenario, Scenario.key == key)
        except Exception as error:
            logging.error(f"Error in CRUDScenario.get_by_key: {error}")
            raise error

    async def list_active(self) -> list[Scenario]:
        """List all active scenario records ordered by insertion order.

        Returns:
            list[Scenario]: Active scenarios available for training.

        Raises:
            Exception: If the database read fails.
        """
        try:
            logging.info("Executing CRUDScenario.list_active")
            return await get_engine().find(Scenario, Scenario.is_active == True)
        except Exception as error:
            logging.error(f"Error in CRUDScenario.list_active: {error}")
            raise error

    async def update(self, *, id: str, obj_in: dict) -> Scenario | None:
        """Update an existing scenario record by identifier.

        Args:
            id (str): Scenario identifier.
            obj_in (dict): Fields to update.

        Returns:
            Scenario | None: Updated scenario model or None when not found.

        Raises:
            HTTPException 400: If the identifier is invalid.
            Exception: If the database update fails.
        """
        try:
            logging.info("Executing CRUDScenario.update")
            scenario = await self.get_by_id(id=id)
            if scenario is None:
                logging.warning(f"No scenario found with id: {id}")
                return None

            for field, value in obj_in.items():
                setattr(scenario, field, value)
            scenario.updated_at = get_utc_now()

            await get_engine().save(scenario)
            return scenario
        except HTTPException:
            raise
        except Exception as error:
            logging.error(f"Error in CRUDScenario.update: {error}")
            raise error
