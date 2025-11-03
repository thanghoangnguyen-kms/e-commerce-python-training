from fastapi import APIRouter, Query, Depends, HTTPException
from app.api.service_deps import get_payment_service, get_order_service
from app.services.payment_service import MockPaymentService
from app.services.order_service import OrderService
from app.api.deps import get_current_user
from app.schemas.payment import PaymentConfirmResponse

router = APIRouter()

@router.post("/confirm", response_model=PaymentConfirmResponse)
async def confirm_payment(
    order_id: str = Query(..., example="67123abc456def789012345", description="Order ID to confirm payment for"),
    outcome: str = Query("success", example="success", description="Payment outcome: success, failure, or canceled"),
    user=Depends(get_current_user),
    payment_service: MockPaymentService = Depends(get_payment_service),
    order_service: OrderService = Depends(get_order_service)
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
    order = await order_service.get_order_by_id(order_id, user["sub"])
    if not order:
        raise HTTPException(404, "Order not found")

    # Process payment
    order = await payment_service.confirm(order_id, outcome)  # type: ignore
    return PaymentConfirmResponse(order_id=str(order.id), status=order.status)
