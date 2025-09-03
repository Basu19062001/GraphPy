from fastapi import APIRouter, Body, status, HTTPException
from fastapi.responses import JSONResponse

from app.schemas.responses import APIResponseModel
from app.schemas.products import CreateProductModel
from app.logger import logger
from app.core.db import collection

router = APIRouter()

products_collection = collection("products")

@router.post("/add-product", response_model=APIResponseModel, summary="Add a new product")
async def add_product(product_payload: CreateProductModel = Body(..., description="Product payload")):
    try:
        product_data = product_payload.model_dump()
        model = product_data.get("model")
        
        existing_product = await products_collection.find_one({"model":model })
        if existing_product:
            inserted_result = await products_collection.update_one(
                {"model": model}, 
                {"$set":{
                    "qty": existing_product["qty"] + product_data.get("qty")
                    }
                }
            )
            if inserted_result.modified_count == 1:
                existing_product["_id"] = str(existing_product["_id"])
                return JSONResponse(
                    status_code=status.HTTP_201_CREATED,
                    content={
                        "message": "Product stock updated successfully",
                        "status": True,
                        "data": product_data,
                    },
                )
            else:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update product stock") 

        inserted_result = await products_collection.insert_one(product_data)
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "message": "Product added successfully",
                "status": True,
                "data": product_data,
            },
        )
    
    except HTTPException as http_err:
        logger.error(f"HTTP error during adding product: {http_err.detail}")
        raise http_err

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid payload. Error: {str(e)}")
