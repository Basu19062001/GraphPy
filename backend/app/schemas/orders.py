from typing import List, Dict

from pydantic import BaseModel, Field


class ProductModel(BaseModel):
    product_id: str = Field(..., description="Unique ID of the product being ordered")
    qty: int = Field(..., gt=0, description="Quantity of the product (must be greater than 0)")


class CreateOrderModel(BaseModel):
    products: List[ProductModel] = Field(
        ..., min_items=1, description="List of products to include in the order (must contain at least one product"
    )
    shipping_addr: str = Field(..., min_length=5, description="Full shipping address where the order should be delivered")
