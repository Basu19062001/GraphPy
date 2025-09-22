import strawberry
from typing import List

from pydantic import Field



@strawberry.type
class Order:
    id: str = Field(..., description="Unique identifier for the order")
    name: str = Field(..., description="Name of the product")
    qty: int = Field(..., description="Quantity of the product ordered", ge=1)
    total_price: float = Field(..., description="Total price of this order", ge=0)

@strawberry.type
class UserOrderTypes:
    id: str = Field(..., description="User id of the product")
    name: str = Field(..., description="Name of the user")
    shapping_address: str = Field(..., description="Shipping address of the user")
    status: str = Field(..., description="Status of the user")
    orders: List[Order] = Field(..., description="User order details")