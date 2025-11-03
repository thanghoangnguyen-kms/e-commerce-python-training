"""Order service for order retrieval and management."""
from app.db.models.order import Order
from app.repositories.order_repository import OrderRepository
from app.core.service_decorator import service_method
from fastapi import HTTPException


class OrderService:
    """
    Service layer for order operations.
    Handles order retrieval and management with user authorization.
    """

    def __init__(self, order_repository: OrderRepository = None):
        """Initialize OrderService with repository dependency."""
        self.order_repository = order_repository or OrderRepository()

    @service_method
    async def get_user_orders(self, user_id: str, skip: int = 0, limit: int = 20) -> list[Order]:
        """
        Get all orders for a specific user with pagination.

        Args:
            user_id: User's MongoDB ObjectId string
            skip: Number of orders to skip for pagination
            limit: Maximum number of orders to return

        Returns:
            List of Order model objects with MongoDB id fields
        """
        orders = await self.order_repository.find_by_user_id(user_id, skip, limit)
        return orders

    @service_method
    async def get_order_by_id(self, order_id: str, user_id: str) -> Order:
        """
        Get a specific order by ID with user authorization.

        Args:
            order_id: Order's MongoDB ObjectId string
            user_id: User's MongoDB ObjectId string for authorization

        Returns:
            Order model object with MongoDB id field

        Raises:
            HTTPException: If order not found or doesn't belong to user
        """
        order = await self.order_repository.find_by_id_and_user(order_id, user_id)
        if not order:
            raise HTTPException(404, "Order not found")
        return order

    @service_method
    async def get_all_orders(self, skip: int = 0, limit: int = 50) -> list[Order]:
        """
        Get all orders in the system (admin only).

        Args:
            skip: Number of orders to skip for pagination
            limit: Maximum number of orders to return

        Returns:
            List of Order model objects with MongoDB id fields
        """
        orders = await self.order_repository.find_all(skip=skip, limit=limit)
        return orders
