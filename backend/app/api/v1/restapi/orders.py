from fastapi import APIRouter, HTTPException, status, Body, Depends

from app.schemas.responses import APIListResponseModel, APIResponseModel
from app.schemas.orders import CreateOrderModel
from app.core.db import collection

router = APIRouter()

orders_collection = collection("orders")
users_collection = collection("users")
products_collection = collection("products")


@router.post("/create-orders", response_model=APIResponseModel, summary="Create order api")
async def order_place(order_payload: CreateOrderModel = Body(..., description="Order creation API")):
    pass
