from fastapi import APIRouter, status, HTTPException, Body
from fastapi.responses import JSONResponse

from app.logger import logger
from app.schemas.users import UserCreateModel

router = APIRouter()


@router.post("/add-user", response_model=dict, summary="Add a new user")
async def add_user(user_payload: UserCreateModel = Body(..., description="User details")):
    pass
