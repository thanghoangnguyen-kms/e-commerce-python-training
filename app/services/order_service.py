from app.db.models.order import Order
from fastapi import HTTPException


class OrderService:
    """
    Service layer for order operations.
    Handles order retrieval and management.
    """

    @staticmethod
    async def get_user_orders(user_id: str, skip: int = 0, limit: int = 20) -> list[Order]:
        """Get all orders for a specific user with pagination."""
        orders = await Order.find(Order.user_id == user_id).skip(skip).limit(limit).to_list()
        return orders

    @staticmethod
    async def get_order_by_id(order_id: str, user_id: str) -> Order:
        """
        Get a specific order by ID.
        Validates that the order belongs to the user.
        """
        order = await Order.get(order_id)
        if not order:
            raise HTTPException(404, "Order not found")

        # Verify ownership
        if order.user_id != user_id:
            raise HTTPException(403, "Not your order")

        return order

    @staticmethod
    async def get_all_orders(skip: int = 0, limit: int = 50) -> list[Order]:
        """Get all orders (admin only)."""
        orders = await Order.find().skip(skip).limit(limit).to_list()
        return orders

