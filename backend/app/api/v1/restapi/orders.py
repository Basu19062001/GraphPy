from fastapi import APIRouter, HTTPException, status

from app.schemas.responses import APIListResponseModel, APIResponseModel

router = APIRouter()


@router.post("/create-orders", response_model=APIResponseModel, summary="Create order api")
async def order_place():
    pass
