from fastapi import APIRouter, HTTPException, status, Body
from fastapi.responses import JSONResponse

from app.core.db import collection
from app.schemas.responses import APIResponseModel
from app.schemas.auth import UserSignupModel
from app.logger import logger

router = APIRouter()

users_collection = collection("users")


@router.post("/signup", response_model=APIResponseModel, summary="User signup API")
async def signup(user_payload: UserSignupModel = Body(..., description="User signup payload")):
    try:
        user_data = user_payload.model_dump()
    except HTTPException as http_err:
        logger.error(f"HTTP error during payload parsing: {http_err.detail}")
        raise http_err
    except Exception as e:
        logger.error(f"Unexpected error during payload parsing: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid payload. Error: {str(e)}")
        