from fastapi import APIRouter

from app.api.v1 import *

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth/user", tags=["Users Authentication APIs"])
