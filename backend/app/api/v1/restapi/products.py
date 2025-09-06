from fastapi import APIRouter, Body, status, HTTPException, Query, Path
from fastapi.responses import JSONResponse

from app.schemas.responses import APIResponseModel, APIListResponseModel
from app.schemas.products import CreateProductModel, GetProductResponseModel
from app.logger import logger
from app.core.db import collection
from app.utils.utils import validate_object_id

router = APIRouter()

products_collection = collection("products")


@router.post("/add-product", response_model=APIResponseModel, summary="Add a new product")
async def add_product(product_payload: CreateProductModel = Body(..., description="Product payload")):
    try:
        product_data = product_payload.model_dump()
        model = product_data.get("model")

        existing_product = await products_collection.find_one({"model": model})
        if existing_product:
            inserted_result = await products_collection.update_one(
                {"model": model}, {"$set": {"qty": existing_product["qty"] + product_data.get("qty")}}
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


@router.get("/", response_model=APIListResponseModel[GetProductResponseModel], summary="Get all products")
async def get_all_products(
    page: int = Query(1, ge=1, description="Page number, starting from 1"),
    limit: int = Query(10, ge=1, le=100, description="Number of products per page, max 100"),
):
    try:
        skip = (page - 1) * limit

        pipeline = [{"$facet": {"metadata": [{"$count": "total"}], "data": {{"$skip": skip}, {"$limit": limit}}}}]

        result = await products_collection.aggregate(pipeline).to_list(length=None)

        if not result:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No products founds")

        metadata = result[0].get("metadata", list())
        products = result[0].get("data", list())

        total_products = metadata[0].get("total", 0) if metadata else 0

        if total_products == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No products found")

        if not products:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No products found for the given page and limit")

        for product in products:
            product["_id"] = str(product.get("_id", ""))

        total_pages = (total_products + limit - 1) // limit

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Products retrieved successfully",
                "status": True,
                "page": page,
                "limit": limit,
                "total": total_products,
                "total_pages": total_pages,
                "data": products,
            },
        )

    except HTTPException as http_err:
        logger.error(f"HTTP error during fetching products: {http_err.detail}")
        raise http_err
    except Exception as e:
        logger.error(f"Unexpected error during fetching products: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to fetch products")


@router.get("/details/{product_id}", response_model=APIListResponseModel, summary="Get product by id")
async def get_product_by_id(product_id: str = Path(..., description="Mongo id of product")):
    try:
        product_oid = validate_object_id(product_id)

        product_details = await products_collection.find_one({"_id":product_oid})

        if not product_details:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"")
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Get product details successfully",
                "status": True,
                "data":product_details
            }
        )
    
    except HTTPException as http_err:
        logger.error(f"")
        raise http_err
    except Exception as e:
        logger.error("")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"")

