from typing import List, Dict, Optional

from pydantic import BaseModel, Field


class ProductModel(BaseModel):
    product_id: str = Field(..., description="Unique ID of the product being ordered")
    qty: int = Field(..., gt=0, description="Quantity of the product (must be greater than 0)")


class CreateOrderModel(BaseModel):
    products: List[ProductModel] = Field(
        ..., min_items=1, description="List of products to include in the order (must contain at least one product"
    )
    shipping_addr: str = Field(..., min_length=5, description="Full shipping address where the order should be delivered")

class OrderResponseModel(BaseModel):
    order_id: str = Field(..., alias="_id", description="Unique identifier for the order")
    name: str = Field(..., description="Name of the product")
    qty: int = Field(..., description="Quantity of the product ordered", ge=1)
    total_price: float = Field(..., description="Total price of this order", ge=0)

    class Config:
        validate_by_name = True
        json_schema_extra = {
            "example":{
                "_id": "550e8400-e29b-41d4-a716-446655440000",
                "product_name": "Wireless Mouse",
                "quantity": 2,
                "total_price": 1499.00
            }
        }

class GetUserOrderResponseModel(BaseModel):
    user_id: str = Field(..., alias="_id", description="User id of the product")
    name: str = Field(..., description="Name of the user")
    shipping_address: str = Field(..., description="Shipping address of the user")
    status: str = Field(..., description="Status of the user")
    orders: List[OrderResponseModel] = Field(..., description="User order details")

    class Config:
        json_schema_extra = {
            "example":{
                "user_id": "123e4567-e89b-12d3-a456-426614174000",
                "name": "John Doe",
                "shipping_address": "123, Park Street, Kolkata",
                "status": "shipped",
                "orders": [
                    {
                        "_id": "550e8400-e29b-41d4-a716-446655440000",
                        "product_name": "Wireless Mouse",
                        "quantity": 2,
                        "total_price": 1499.00
                    },
                    {
                        "_id": "650e8400-e29b-41d4-a716-446655440111",
                        "product_name": "Mechanical Keyboard",
                        "quantity": 1,
                        "total_price": 3499.00
                    }
                ]
            }
        }
