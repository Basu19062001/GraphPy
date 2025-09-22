from typing import List

from fastapi import APIRouter, HTTPException, status, Body, Depends, Path
from fastapi.responses import JSONResponse

from app.schemas.responses import APIListResponseModel, APIResponseModel
from app.schemas.orders import CreateOrderModel, GetUserOrderResponseModel, OrderResponseModel
from app.core.db import collection
from app.utils.auth_utils import auth_services
from app.utils.utils import validate_object_id, get_current_utc_time, serialize_data
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


@router.get(
    "/user/{user_id}/get-orders",
    response_model=APIListResponseModel[GetUserOrderResponseModel],
    summary="Get order of the user",
)
async def get_user_orders(user_id: str = Path(..., description="User Id of the product")):
    try:
        user_oid = validate_object_id(user_id, error_msg="Invalid user id format")

        user_doc = await users_collection.find_one({"_id": user_oid})

        if not user_doc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User with id not found")

        order_cursor = orders_collection.find({"user_id": user_oid})
        orders = await order_cursor.to_list(length=None)

        if not orders:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No orders found for the user {user_id}")

        user_orders: List[GetUserOrderResponseModel] = []

        for order in orders:
            order_items = []
            for product in order.get("products", []):
                order_items.append(
                    OrderResponseModel(
                        order_id=str(order.get("_id")),
                        name=product.get("name", ""),
                        qty=product.get("quantity", None),
                        total_price=product.get("price", None),
                    )
                )

                user_orders.append(
                    GetUserOrderResponseModel(
                        user_id=str(user_doc.get("_id")),
                        name=user_doc.get("full_name", ""),
                        shipping_address=order.get("shipping_address", ""),
                        status=order.get("status"),
                        orders=order_items,
                    )
                )

        serialied_orders = serialize_data([order.model_dump() for order in user_orders])

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": f"Found {len(user_orders)} orders for user {user_doc.get("full_name")}",
                "status": True,
                "data": serialied_orders,
            },
        )

    except HTTPException as http_err:
        logger.error(f"Error while fetching order {http_err.detail}")
        raise http_err

    except Exception as e:
        logger.error(f"Unexpected error occrrued while fetching order for the user: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error {str(e)}")
