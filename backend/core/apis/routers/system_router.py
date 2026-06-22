"""Infrastructure routes for backend readiness and health checks."""

from fastapi import APIRouter, HTTPException, status

from commons.logger import logger

system_router = APIRouter(tags=["system"])
logging = logger(__name__)


@system_router.get("/", status_code=status.HTTP_200_OK)
async def root() -> dict[str, str]:
    """Return a simple backend readiness message.

    Provides a lightweight root endpoint so local startup can be verified
    without relying on business-domain routes.

    Returns:
        dict[str, str]: Basic backend readiness payload.

    Raises:
        HTTPException 500: If the route fails unexpectedly.
    """
    try:
        logging.info("Calling GET / endpoint")
        return {"message": "SalesPilot AI backend is running"}
    except HTTPException as httperror:
        logging.error(f"Error in GET / endpoint: {httperror}")
        raise httperror
    except Exception as error:
        logging.error(f"Error in GET / endpoint: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )


@system_router.get("/health", status_code=status.HTTP_200_OK)
async def health_check() -> dict[str, str]:
    """Return a health status payload for uptime checks.

    Exposes a minimal infrastructure endpoint used to confirm the API process
    is reachable and serving requests.

    Returns:
        dict[str, str]: Health indicator payload.

    Raises:
        HTTPException 500: If the route fails unexpectedly.
    """
    try:
        logging.info("Calling GET /health endpoint")
        return {"status": "healthy"}
    except HTTPException as httperror:
        logging.error(f"Error in GET /health endpoint: {httperror}")
        raise httperror
    except Exception as error:
        logging.error(f"Error in GET /health endpoint: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal Server Error",
        )
