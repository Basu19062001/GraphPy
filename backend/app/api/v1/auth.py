from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from app.core.db import collection

router = APIRouter()

users_collection = collection("users")


@router.post("/signup",response_model= dict, summary="User signup API")
async def signup():
    pass