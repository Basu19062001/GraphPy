from pydantic import BaseModel, Field


class CreateProductModel(BaseModel):
    name: str = Field(..., description="Name of the product")
    title: str = Field(..., description="Title of the product")
    description: str = Field(..., description="Description of the product")
    price: float = Field(..., description="Price of the product")
    stock: int = Field(..., description="Stock quantity of the product")
    category: str = Field(..., description="Category of the product")
    brand: str = Field(..., description="Brand of the product")

    class config:
        schema_extra = {
            "example": {
                "name": "Sample Product",
                "title": "This is a sample product",
                "description": "Detailed description of the sample product",
                "price": 29.99,
                "stock": 100,
                "category": "Electronics",
                "brand": "SampleBrand",
            }
        }
