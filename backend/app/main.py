from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from uvicorn import run

from app.logger import logger
from app.core.config import settings

app = FastAPI()


@app.get("/api/health", summary="Health Check", tags="System")
async def health_check():
    logger.info("Health check endpoint called")
    return JSONResponse(
        status_code=status.HTTP_200_OK, content={"message": "Healthy", "status": True, "version": settings.VERSION}
    )


if __name__ == "__main__":
    run(app, host="0.0.0.0", port=8000, log_config=None)
