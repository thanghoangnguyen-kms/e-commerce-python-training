from fastapi import APIRouter, Depends, Query, Path
from app.api.deps import get_current_user, admin_required
from app.services.order_service import OrderService

router = APIRouter()

@router.get("")
async def get_user_orders(
    user=Depends(get_current_user),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of items to return")
):
    """
    Get all orders for the current user.

    Returns a paginated list of orders with order details.
    """
    orders = await OrderService.get_user_orders(user["sub"], skip, limit)
    return orders

@router.get("/{order_id}")
async def get_order_details(
    order_id: str = Path(..., example="67123abc456def789012345", description="Order ID"),
    user=Depends(get_current_user)
):
    """
    Get detailed information about a specific order.

    Only returns the order if it belongs to the authenticated user.
    """
    order = await OrderService.get_order_by_id(order_id, user["sub"])
    return order

@router.get("/admin/all")
async def get_all_orders_admin(
    _=Depends(admin_required),
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of items to return")
):
    """
    Get all orders in the system (Admin only).

    Returns a paginated list of all orders across all users.
    """
    orders = await OrderService.get_all_orders(skip, limit)
    return orders

