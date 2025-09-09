from fastapi import APIRouter, HTTPException, status, Body, Depends
from fastapi.responses import JSONResponse

from app.schemas.responses import APIListResponseModel, APIResponseModel
from app.schemas.orders import CreateOrderModel
from app.core.db import collection
from app.utils.auth_utils import auth_services
from app.utils.utils import validate_object_id, get_current_utc_time
from app.logger import logger

router = APIRouter()

orders_collection = collection("orders")
users_collection = collection("users")
products_collection = collection("products")


@router.post("/create-orders", response_model=APIResponseModel, summary="Create order api")
async def order_place(
    order_payload: CreateOrderModel = Body(..., description="Order creation API"),
    user_payload: dict = Depends(auth_services.get_current_user),
):
    try:
        logger.debug(f"user_payload: {user_payload}")
        user_id = user_payload.get("sub", "")

        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized user")

        user_oid = validate_object_id(user_id, error_msg="Invalid object id")

        order_products = list()
        for item in order_payload.products:
            product_oid = validate_object_id(item.product_id, error_msg="Invalid Product Id Format")
            product = await products_collection.find_one({"_id": product_oid})

            if not product:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=f"Product with id {item.product_id} not found"
                )

            if product.get("qty", 0) < item.qty:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=f"Insufficient stock for product {product.get('name', '')}"
                )

            order_products.append(
                {
                    "product_id": str(product["_id"]),
                    "name": product.get("name"),
                    "quantity": item.qty,
                    "price": product.get("price"),
                }
            )

        order_doc = {
            "user_id": user_oid,
            "products": order_products,
            "shipping_address": order_payload.shipping_addr,
            "status": "pending",
            "created_at": get_current_utc_time(),
            "updated_at": get_current_utc_time(),
        }

        result = await orders_collection.insert_one(order_doc)
        order_id = str(result.inserted_id)

        for item in order_payload.products:
            await products_collection.update_one({"_id": validate_object_id(item.product_id)}, {"$inc": {"qty": -item.qty}})

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Order placed sucessfully", "status": True, "data": {"order_id": order_id}},
        )

    except HTTPException as http_err:
        logger.error("HTTPException while placing order: {http_err.detail}")
        raise http_err
    except Exception as e:
        logger.error(f"Error occurred while creating order: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unexpected error while placing order: {str(e)}"
        )
