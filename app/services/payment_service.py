"""Payment service for order payment processing."""
from typing import Literal

from app.db.models.order import Order
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.core.service_decorator import service_method
from fastapi import HTTPException

PaymentOutcome = Literal["success", "failure", "canceled"]


class MockPaymentService:
    """
    Mock payment service for testing and development.

    Business rules:
      - Only transition from 'pending' -> 'paid'/'failed'/'canceled'
      - On 'paid', decrement inventory for each item
      - Idempotent: If order already finalized, return without changes

    Note: Replace this with a real payment gateway integration in production.
    """

    def __init__(
        self, 
        order_repository: OrderRepository = None, 
        product_repository: ProductRepository = None
    ):
        """Initialize MockPaymentService with repository dependencies."""
        self.order_repository = order_repository or OrderRepository()
        self.product_repository = product_repository or ProductRepository()

    @service_method
    async def confirm(self, order_id: str, outcome: PaymentOutcome = "success") -> Order:
        """
        Confirm payment for an order.

        Args:
            order_id: The MongoDB ObjectId string of the order to process payment for
            outcome: Payment outcome (success, failure, or canceled)

        Returns:
            Updated Order model object with new status and MongoDB id field

        Raises:
            HTTPException: If order not found or insufficient inventory
        """
        order = await self.order_repository.get_by_id(order_id)
        if not order:
            raise HTTPException(404, "Order not found")

        if order.status != "pending":
            # Idempotent - do nothing if already finalized
            return order

        if outcome == "success":
            # Decrement inventory for each order item
            # Note: Order items store MongoDB ObjectId strings
            for item in order.items:
                product = await self.product_repository.get_by_id(item.product_id)
                if not product or product.inventory < item.qty:
                    order.status = "failed"
                    await self.order_repository.update(order)
                    raise HTTPException(400, f"Insufficient inventory for product {item.name}")

                # Decrement inventory using repository method (uses MongoDB ObjectId string)
                await self.product_repository.decrement_inventory(item.product_id, item.qty)

            order.status = "paid"
        elif outcome == "canceled":
            order.status = "canceled"
        else:
            order.status = "failed"

        await self.order_repository.update(order)
        return order
