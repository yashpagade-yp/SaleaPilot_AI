"""Runtime entrypoint for starting the SalesPilot FastAPI backend."""

import os

from dotenv import load_dotenv
import uvicorn

from commons.logger import logger
from core.apis.api import app

load_dotenv()

logging = logger(__name__)


def run() -> None:
    """Start the local Uvicorn server for the backend application.

    Reads host, port, and reload preferences from environment variables so
    the backend can be started consistently across local environments.

    Raises:
        ValueError: If the configured API port cannot be converted to an integer.
    """
    logging.info("Executing main.run")
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    reload_enabled = os.getenv("API_RELOAD", "true").lower() == "true"

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload_enabled,
    )


if __name__ == "__main__":
    run()
