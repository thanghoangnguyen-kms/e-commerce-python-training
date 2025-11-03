"""Cart request/response schemas."""
from pydantic import BaseModel, Field


class CartItemRequest(BaseModel):
    """Request schema for adding items to cart."""
    product_id: int = Field(..., example=1, description="Product ID to add (integer product_id, not MongoDB _id)")
    qty: int = Field(..., gt=0, example=2, description="Quantity of the product")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "product_id": 1,
                    "qty": 2
                }
            ]
        }
    }


class CartRemoveRequest(BaseModel):
    """Request schema for removing items from cart."""
    product_id: int = Field(..., example=1, description="Product ID to remove (integer product_id, not MongoDB _id)")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "product_id": 1
                }
            ]
        }
    }
