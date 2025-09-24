import time
from typing import List

from app.core.db import collection
from app.schemas.orders import CreateOrderModel, GetUserOrderResponseModel, OrderResponseModel
from app.utils.utils import validate_object_id, get_current_utc_time

orders_collection = collection("orders")
users_collection = collection("users")
products_collection = collection("products")

class OrderService:

    @classmethod
    async def place_order(cls, user_id: str, order_payload: CreateOrderModel):
        user_oid = validate_object_id(user_id, error_msg="Invalid object id")
        user_doc = await users_collection.find_one({"_id": user_oid})
        if not user_doc:
            raise ValueError("User not found")

        order_products = list()
        for item in order_payload.products:

            product_oid = validate_object_id(item.product_id, error_msg="Invalid Product Id Format")
            product = await products_collection.find_one({"_id": product_oid})
            if not product:
                raise ValueError(f"Product {item.product_id} not found")
            if product.get("qty", 0) < item.qty:
                raise ValueError(f"Insufficient stock for product {product.get('name')}")
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

        return order_id


    async def get_user_orders(cls, user_id: str) -> List[GetUserOrderResponseModel]:
        user_oid = validate_object_id(user_id, error_msg="Invalid user id format")
        user_doc = await users_collection.find_one({"_id": user_oid})
        if not user_doc:
            return list()

        orders_cursor = orders_collection.find({"user_id": user_oid})
        orders = await orders_cursor.to_list(length=None)

        user_orders = list()
        for order in orders:
            items = list()
            for p in order.get("products", list()):
                items.append(
                    OrderResponseModel(
                        order_id=str(order.get("_id")),
                        name=p.get("name", ""),
                        qty=p.get("quantity", 0),
                        total_price=p.get("price", 0.0),
                    )
                )
            user_orders.append(
                GetUserOrderResponseModel(
                    user_id=str(user_doc.get("_id")),
                    name=user_doc.get("full_name", ""),
                    shipping_address=order.get("shipping_address", ""),
                    status=order.get("status", ""),
                    orders=items,
                )
            )
        
        return user_orders
