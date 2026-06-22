"""FastAPI application wiring for the SalesPilot backend."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from commons.logger import logger
from core.apis.routers.system_router import system_router
from core.database.database import connect_to_mongo, disconnect_from_mongo

logging = logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Manage application startup and shutdown resources.

    Opens shared infrastructure such as the MongoDB connection before serving
    requests and closes them gracefully during shutdown.

    Args:
        _ (FastAPI): FastAPI application instance supplied by the framework.

    Yields:
        None: Control back to the FastAPI application runtime.
    """
    logging.info("Executing application lifespan startup")
    await connect_to_mongo()
    try:
        yield
    finally:
        logging.info("Executing application lifespan shutdown")
        await disconnect_from_mongo()


app = FastAPI(
    title="SalesPilot AI Backend",
    version="0.1.0",
    lifespan=lifespan,
)
app.include_router(system_router)
