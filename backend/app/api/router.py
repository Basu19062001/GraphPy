from fastapi import APIRouter

from app.api.v1 import *

api_router = APIRouter()

# api_router.include_router(users_router, prefix="/users", tags=["Users Management APIs"])
