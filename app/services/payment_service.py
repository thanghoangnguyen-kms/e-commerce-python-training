from typing import Literal
from app.db.models.order import Order
from app.db.models.product import Product

PaymentOutcome = Literal["success", "failure", "canceled"]

class MockPaymentService:
    """
    A stub you can replace with a real gateway later.
    Business rules:
      - Only transition from 'pending' -> 'paid'/'failed'/'canceled'
      - On 'paid', decrement inventory for each item
    """

    @staticmethod
    async def confirm(order_id: str, outcome: PaymentOutcome = "success") -> Order:
        order = await Order.get(order_id)
        if not order:
            raise ValueError("Order not found")

        if order.status not in ("pending",):
            # idempotent - do nothing if already finalized
            return order

        if outcome == "success":
            # Decrement inventory (simple logic; not concurrency-safe yet)
            for it in order.items:
                prod = await Product.get(it.product_id)
                if not prod or prod.inventory < it.qty:
                    order.status = "failed"
                    await order.save()
                    return order
                prod.inventory -= it.qty
                await prod.save()
            order.status = "paid"
        elif outcome == "canceled":
            order.status = "canceled"
        else:
            order.status = "failed"

        await order.save()
        return order
