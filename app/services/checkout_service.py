from app.db.models.order import Order, OrderItem
from app.db.models.cart import Cart
from app.db.models.product import Product
from fastapi import HTTPException


class CheckoutService:
    """
    Service layer for checkout operations.
    Handles order creation from cart items.
    """

    @staticmethod
    async def create_order_from_cart(user_id: str) -> Order:
        """
        Create an order from the user's cart.
        Validates all products are available and calculates totals.
        """
        # Get user's cart
        cart = await Cart.find_one(Cart.user_id == user_id)
        if not cart or not cart.items:
            raise HTTPException(400, "Cart is empty")

        order_items: list[OrderItem] = []
        total = 0.0

        # Process each cart item
        for cart_item in cart.items:
            product = await Product.get(cart_item.product_id)

            # Validate product availability
            if not product or not product.is_active:
                raise HTTPException(400, f"Item unavailable: {cart_item.product_id}")

            # Calculate line total
            line_total = product.price * cart_item.qty
            total += line_total

            # Create order item
            order_items.append(OrderItem(
                product_id=str(product.id),
                name=product.name,
                unit_price=product.price,
                qty=cart_item.qty,
                line_total=line_total
            ))

        # Create order
        order = Order(user_id=user_id, items=order_items, total=total)
        await order.insert()

        # Clear cart after successful order creation
        cart.items = []
        await cart.save()

        return order

