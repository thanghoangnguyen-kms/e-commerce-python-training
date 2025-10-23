from fastapi import APIRouter, Query, Depends, HTTPException
from app.services.payment_service import MockPaymentService
from app.api.deps import get_current_user
from app.db.models.order import Order
from app.schemas.payment import PaymentConfirmResponse

router = APIRouter()

@router.post("/confirm", response_model=PaymentConfirmResponse)
async def confirm_payment(
    order_id: str = Query(..., example="67123abc456def789012345", description="Order ID to confirm payment for"),
    outcome: str = Query("success", example="success", description="Payment outcome: success, failure, or canceled"),
    user=Depends(get_current_user)
):
    """
    Confirm payment for an order (Mock endpoint).

    Simulates payment processing. On success, decrements inventory and marks order as paid.

    **Outcomes:**
    - `success`: Payment successful, order marked as paid
    - `failure`: Payment failed, order marked as failed
    - `canceled`: Payment canceled by user
    """
    # Verify order ownership - SECURITY FIX
    order = await Order.get(order_id)
    if not order:
        raise HTTPException(404, "Order not found")

    if order.user_id != user["sub"]:
        raise HTTPException(403, "Not your order")

    # Process payment
    order = await MockPaymentService.confirm(order_id, outcome)  # type: ignore
    return PaymentConfirmResponse(order_id=str(order.id), status=order.status)
