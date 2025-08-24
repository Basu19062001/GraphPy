from fastapi import FastAPI, status, HTTPException
from fastapi.responses import JSONResponse
from uvicorn import run
from fastapi.security import HTTPBasic
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.exceptions import RequestValidationError

from app.logger import logger
from app.core.config import settings
from app.middleware.log_middleware import log_request_middleware
from app.common.exception_handler import (
    request_validation_exception_handler,
    http_exception_handler,
    unhandled_exception_handler,
)
from app.api.router import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

security = HTTPBasic()

# Add SessionMiddleware for OAuth
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.JWT_SECRET_KEY,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
    expose_headers=["*"],
    max_age=3600,  # Cache preflight requests for 1 hour
)

app.middleware("http")(log_request_middleware)
app.add_exception_handler(RequestValidationError, request_validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

# Include All Routers
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/api/health", summary="Health Check", tags="System")
async def health_check():
    logger.info("Health check endpoint called")
    return JSONResponse(
        status_code=status.HTTP_200_OK, content={"message": "Healthy", "status": True, "version": settings.VERSION}
    )


if __name__ == "__main__":
    run(app, host="0.0.0.0", port=8000, log_config=None)
