from fastapi import APIRouter

from app.api.v1 import *

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth/users", tags=["Users Authentication APIs"])
api_router.include_router(products_router, prefix="/products", tags=["Products Management APIs"])
api_router.include_router(order_router, prefix="/orders", tags=["Order management APIs"])
