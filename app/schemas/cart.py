"""Cart request/response schemas."""
from pydantic import BaseModel, Field


class CartItemRequest(BaseModel):
    """Request schema for adding items to cart."""
    product_id: str = Field(..., example="67123abc456def789012345", description="Product ID to add")
    qty: int = Field(..., gt=0, example=2, description="Quantity of the product")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "product_id": "67123abc456def789012345",
                    "qty": 2
                }
            ]
        }
    }


class CartRemoveRequest(BaseModel):
    """Request schema for removing items from cart."""
    product_id: str = Field(..., example="67123abc456def789012345", description="Product ID to remove")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "product_id": "67123abc456def789012345"
                }
            ]
        }
    }


