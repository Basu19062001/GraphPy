from fastapi import APIRouter

router = APIRouter()


@router.post("/add-product")
async def add_product():
    pass