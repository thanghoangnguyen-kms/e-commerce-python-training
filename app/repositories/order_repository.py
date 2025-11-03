"""
Order repository for order-related data access operations.
"""
from app.repositories.base_repository import BaseRepository
from app.db.models.order import Order


class OrderRepository(BaseRepository[Order]):
    """Repository for Order model operations."""

    def __init__(self):
        super().__init__(Order)

    async def find_by_user_id(self, user_id: str, skip: int = 0, limit: int = 20) -> list[Order]:
        """Find all orders for a specific user."""
        return await self.find_many(Order.user_id == user_id, skip=skip, limit=limit)

    async def find_by_id_and_user(self, order_id: str, user_id: str) -> Order | None:
        """Find an order by ID and verify it belongs to the user."""
        # First get the order by ID, then verify it belongs to the user
        order = await self.get_by_id(order_id)
        if order and order.user_id == user_id:
            return order
        return None

    async def update_status(self, order_id: str, status: str) -> Order | None:
        """Update the status of an order."""
        order = await self.get_by_id(order_id)
        if order:
            order.status = status
            await self.update(order)
        return order
