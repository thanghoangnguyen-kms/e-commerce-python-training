"""Payment request/response schemas."""
from pydantic import BaseModel, Field


class PaymentConfirmResponse(BaseModel):
    """Response schema for payment confirmation."""
    order_id: str = Field(..., example="67123abc456def789012345", description="Order ID")
    status: str = Field(..., example="paid", description="Payment status (paid/failed/canceled)")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "order_id": "67123abc456def789012345",
                    "status": "paid"
                }
            ]
        }
    }

