"""MongoDB lifecycle and ODMantic engine helpers for the SalesPilot backend."""

from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
import secrets

from bson import ObjectId
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
from odmantic import AIOEngine, Model
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from commons.auth import encrypt_password
from commons.logger import logger
from core.models.conversation_model import Conversation
from core.models.feedback_model import Feedback
from core.models.invitation_model import Invitation
from core.models.scenario_model import Scenario, ScenarioKey
from core.models.training_session_model import TrainingSession
from core.models.user_model import User, UserRole

BACKEND_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE_PATH = BACKEND_ROOT / ".env"

load_dotenv(dotenv_path=ENV_FILE_PATH)

logging = logger(__name__)

DEFAULT_SCENARIOS: list[dict] = [
    {
        "key": ScenarioKey.IDEAL,
        "title": "Ideal Customer",
        "description": "Friendly and interested CRM buyer who helps build confidence.",
        "agent_id": "6a397c577d18fcfe84e9d368",
        "is_active": True,
        "sort_order": 1,
    },
    {
        "key": ScenarioKey.RUDE,
        "title": "Rude Customer",
        "description": "Sharp and skeptical CRM buyer who pressures objection handling.",
        "agent_id": "6a39847f7d18fcfe84e9d8ac",
        "is_active": True,
        "sort_order": 2,
    },
    {
        "key": ScenarioKey.BUSY,
        "title": "Busy Customer",
        "description": "Time-pressed CRM buyer who forces concise pitching and next steps.",
        "agent_id": "6a39855d7d18fcfe84e9d91e",
        "is_active": True,
        "sort_order": 3,
    },
]


class MongoSettings(BaseSettings):
    """Environment-backed MongoDB settings for the backend."""

    mongodb_url: str = Field(..., alias="MONGODB_URL")
    mongodb_database: str = Field(..., alias="MONGODB_DATABASE")
    default_admin_email: str | None = Field(
        default=None,
        alias="DEFAULT_ADMIN_EMAIL",
    )
    default_admin_password: str | None = Field(
        default=None,
        alias="DEFAULT_ADMIN_PASSWORD",
    )

    model_config = SettingsConfigDict(
        env_file=ENV_FILE_PATH,
        extra="ignore",
        populate_by_name=True,
    )


REGISTERED_MODELS: list[type[Model]] = [
    User,
    Scenario,
    TrainingSession,
    Conversation,
    Feedback,
    Invitation,
]

mongo_client: AsyncIOMotorClient | None = None
engine: AIOEngine | None = None


@lru_cache(maxsize=1)
def get_mongo_settings() -> MongoSettings:
    """Return cached MongoDB settings loaded from environment variables.

    Reuses one parsed settings object for the process so CRUD and startup
    code read the same database configuration.

    Returns:
        MongoSettings: Parsed MongoDB settings.
    """
    return MongoSettings()


def get_engine() -> AIOEngine:
    """Return the initialized ODMantic engine.

    Returns:
        AIOEngine: Shared ODMantic engine instance.

    Raises:
        RuntimeError: If the database connection has not been initialized yet.
    """
    if engine is None:
        raise RuntimeError("MongoDB engine is not initialized.")
    return engine


def get_utc_now() -> datetime:
    """Return the current UTC-aware datetime for persistence updates.

    Returns:
        datetime: Current UTC timestamp.
    """
    return datetime.now(timezone.utc)


def generate_placeholder_phone_number() -> str:
    """Generate a unique placeholder phone number for admin/user records.

    Returns:
        str: Random numeric placeholder value.
    """
    return f"9{secrets.randbelow(10**17):017d}"


def parse_object_id(id: str) -> ObjectId:
    """Convert a string identifier into a MongoDB ObjectId.

    Args:
        id (str): MongoDB identifier as a string.

    Returns:
        ObjectId: Parsed MongoDB ObjectId.

    Raises:
        ValueError: If the identifier is not a valid ObjectId.
    """
    try:
        return ObjectId(id)
    except Exception as error:
        raise ValueError("Invalid MongoDB ObjectId.") from error


async def connect_to_mongo() -> None:
    """Connect to MongoDB and initialize the ODMantic engine.

    Opens the shared Motor client, validates connectivity with a ping, and
    configures ODMantic indexes for the registered models.

    Raises:
        Exception: If the MongoDB connection or engine initialization fails.
    """
    global mongo_client, engine

    try:
        logging.info("Executing connect_to_mongo")
        if mongo_client is not None and engine is not None:
            logging.info("MongoDB connection already initialized")
            return

        settings = get_mongo_settings()
        mongo_client = AsyncIOMotorClient(settings.mongodb_url)
        await mongo_client.admin.command("ping")

        engine = AIOEngine(
            client=mongo_client,
            database=settings.mongodb_database,
        )
        await engine.configure_database(models=REGISTERED_MODELS)
        await ensure_default_admin()
        await ensure_default_scenarios()
        logging.info(
            f"MongoDB connected successfully to database {settings.mongodb_database}"
        )
    except Exception as error:
        logging.error(f"Error in connect_to_mongo: {error}")
        raise error


async def ensure_default_scenarios() -> None:
    """Create or update the default SalesPilot scenario records.

    Ensures the three current MVP personas are available in MongoDB with the
    correct Eigi agent mappings when the application starts.

    Raises:
        RuntimeError: If the ODMantic engine has not been initialized.
        Exception: If reading or writing scenario records fails.
    """
    try:
        logging.info("Executing ensure_default_scenarios")
        active_engine = get_engine()

        for payload in DEFAULT_SCENARIOS:
            existing = await active_engine.find_one(
                Scenario,
                Scenario.key == payload["key"],
            )

            if existing is None:
                await active_engine.save(Scenario(**payload))
                logging.info(
                    f"Seeded default scenario for key {payload['key']}"
                )
                continue

            existing.title = payload["title"]
            existing.description = payload["description"]
            existing.agent_id = payload["agent_id"]
            existing.is_active = payload["is_active"]
            existing.sort_order = payload["sort_order"]
            existing.updated_at = get_utc_now()
            await active_engine.save(existing)
            logging.info(
                f"Updated default scenario for key {payload['key']}"
            )
    except Exception as error:
        logging.error(f"Error in ensure_default_scenarios: {error}")
        raise error


async def ensure_default_admin() -> None:
    """Create or update the default admin record from environment settings.

    Ensures the admin login flow uses the configured email and password rather
    than the legacy phone-number-based admin identity.

    Raises:
        RuntimeError: If the ODMantic engine has not been initialized.
        Exception: If reading or writing the admin record fails.
    """
    try:
        logging.info("Executing ensure_default_admin")
        active_engine = get_engine()
        settings = get_mongo_settings()
        admin_email = (settings.default_admin_email or "").strip().lower()
        admin_password = (settings.default_admin_password or "").strip()

        if not admin_email or not admin_password:
            logging.error(
                "Missing DEFAULT_ADMIN_EMAIL or DEFAULT_ADMIN_PASSWORD for admin startup seed"
            )
            raise RuntimeError(
                "DEFAULT_ADMIN_EMAIL and DEFAULT_ADMIN_PASSWORD must be set in "
                "backend/.env for the admin email + password + OTP flow."
            )

        admin_password_hash = encrypt_password(admin_password)

        existing_admin = await active_engine.find_one(
            User,
            User.email == admin_email,
        )

        if existing_admin is None:
            admin_candidates = await active_engine.find(
                User,
                User.role == UserRole.ADMIN,
            )
            if admin_candidates:
                logging.error(
                    "Admin seed email does not match the existing admin record"
                )
                raise RuntimeError(
                    "An admin user already exists with a different email. "
                    "Update DEFAULT_ADMIN_EMAIL to match the existing admin "
                    "record or manually align the database before startup."
                )

        if existing_admin is None:
            await active_engine.save(
                User(
                    first_name="Admin",
                    last_name="User",
                    email=admin_email,
                    phone_number=generate_placeholder_phone_number(),
                    password_hash=admin_password_hash,
                    role=UserRole.ADMIN,
                    is_active=True,
                    otp=None,
                    auth_metadata={
                        "seeded_from_env": True,
                    },
                )
            )
            logging.info(f"Seeded default admin for email {admin_email}")
            return

        existing_admin.first_name = existing_admin.first_name or "Admin"
        existing_admin.last_name = existing_admin.last_name or "User"
        existing_admin.email = admin_email
        existing_admin.phone_number = (
            existing_admin.phone_number or generate_placeholder_phone_number()
        )
        existing_admin.password_hash = admin_password_hash
        existing_admin.role = UserRole.ADMIN
        existing_admin.is_active = True
        existing_admin.otp = None
        existing_admin.auth_metadata = {
            **(existing_admin.auth_metadata or {}),
            "seeded_from_env": True,
        }
        existing_admin.updated_at = get_utc_now()
        await active_engine.save(existing_admin)
        logging.info(f"Updated default admin for email {admin_email}")
    except Exception as error:
        logging.error(f"Error in ensure_default_admin: {error}")
        raise error


async def disconnect_from_mongo() -> None:
    """Close the shared MongoDB client and clear the cached engine.

    Ensures the application releases the Motor client when the FastAPI app
    shuts down.

    Raises:
        Exception: If closing the MongoDB client fails unexpectedly.
    """
    global mongo_client, engine

    try:
        logging.info("Executing disconnect_from_mongo")
        if mongo_client is not None:
            mongo_client.close()
            logging.info("MongoDB connection closed successfully")

        mongo_client = None
        engine = None
    except Exception as error:
        logging.error(f"Error in disconnect_from_mongo: {error}")
        raise error
