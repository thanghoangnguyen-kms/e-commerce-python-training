"""Order request/response schemas."""
from pydantic import BaseModel, Field


class OrderCreateResponse(BaseModel):
    """Response schema for order creation."""
    order_id: str = Field(..., example="67123abc456def789012345", description="Created order ID")
    status: str = Field(..., example="pending", description="Order status")
    total: float = Field(..., example=2999.00, description="Total amount in USD")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "order_id": "67123abc456def789012345",
                    "status": "pending",
                    "total": 2999.00
                }
            ]
        }
    }

