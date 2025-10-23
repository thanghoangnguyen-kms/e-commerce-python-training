from fastapi import APIRouter, Depends
from app.api.deps import get_current_user
from app.services.checkout_service import CheckoutService
from app.schemas.order import OrderCreateResponse

router = APIRouter()

@router.post("/create-order", response_model=OrderCreateResponse)
async def create_order(user=Depends(get_current_user)):
    """
    Create an order from the current user's cart.

    Converts cart items into a pending order. Cart is automatically cleared after order creation.
    Inventory is not decremented until payment is confirmed.
    """
    order = await CheckoutService.create_order_from_cart(user["sub"])
    return OrderCreateResponse(order_id=str(order.id), status=order.status, total=order.total)
