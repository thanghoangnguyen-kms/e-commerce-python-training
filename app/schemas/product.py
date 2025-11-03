"""Product request/response schemas."""
from pydantic import BaseModel, Field


class ProductCreateRequest(BaseModel):
    """Request schema for creating a product."""
    product_id: int = Field(..., example=1001, description="Unique product ID (integer)")
    name: str = Field(..., example="Gaming Laptop Pro", description="Product name")
    slug: str = Field(..., example="gaming-laptop-pro", description="URL-friendly product identifier")
    description: str | None = Field(None, example="High-performance gaming laptop with RTX 4080", description="Product description")
    price: float = Field(..., gt=0, example=1499.99, description="Price in USD (e.g., 1499.99)")
    image: str | None = Field(None, example="https://example.com/images/gaming-laptop-pro.jpg", description="Product image URL")
    inventory: int = Field(default=0, ge=0, example=50, description="Available inventory quantity")
    category: str | None = Field(None, example="Electronics", description="Product category")
    is_active: bool = Field(default=True, example=True, description="Whether product is active and available")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "product_id": 1001,
                    "name": "Gaming Laptop Pro",
                    "slug": "gaming-laptop-pro",
                    "description": "High-performance gaming laptop with RTX 4080 GPU and 32GB RAM",
                    "price": 1499.99,
                    "image": "https://example.com/images/gaming-laptop-pro.jpg",
                    "inventory": 50,
                    "category": "Electronics",
                    "is_active": True
                }
            ]
        }
    }


class ProductUpdateRequest(ProductCreateRequest):
    """Request schema for updating a product."""
    pass


