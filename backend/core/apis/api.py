"""FastAPI application wiring for the SalesPilot backend."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from commons.logger import logger
from core.apis.routers.admin_router import admin_router
from core.apis.routers.auth_router import auth_router
from core.apis.routers.conversation_router import conversation_router
from core.apis.routers.feedback_router import feedback_router
from core.apis.routers.invitation_router import invitation_router
from core.apis.routers.scenario_router import scenario_router
from core.apis.routers.system_router import system_router
from core.apis.routers.training_session_router import training_session_router
from core.database.database import connect_to_mongo, disconnect_from_mongo
from core.services.post_session_service import PostSessionAutomationService

logging = logger(__name__)
post_session_service = PostSessionAutomationService()


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
    await post_session_service.start()
    try:
        yield
    finally:
        logging.info("Executing application lifespan shutdown")
        await post_session_service.stop()
        await disconnect_from_mongo()


app = FastAPI(
    title="SalesPilot AI Backend",
    version="0.1.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(system_router)
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(invitation_router)
app.include_router(scenario_router)
app.include_router(training_session_router)
app.include_router(conversation_router)
app.include_router(feedback_router)
