"""Checkout service for order creation from cart."""
from app.db.models.order import Order, OrderItem
from app.repositories.cart_repository import CartRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.order_repository import OrderRepository
from app.core.service_decorator import service_method
from fastapi import HTTPException


class CheckoutService:
    """
    Service layer for checkout operations.
    Handles order creation from cart items with validation.
    """

    def __init__(
        self, 
        cart_repository: CartRepository = None, 
        product_repository: ProductRepository = None,
        order_repository: OrderRepository = None
    ):
        """Initialize CheckoutService with repository dependencies."""
        self.cart_repository = cart_repository or CartRepository()
        self.product_repository = product_repository or ProductRepository()
        self.order_repository = order_repository or OrderRepository()

    @service_method
    async def create_order_from_cart(self, user_id: str) -> Order:
        """
        Create an order from the user's cart.
        
        Validates all products are available, calculates totals,
        creates the order, and clears the cart.
        
        Args:
            user_id: User's MongoDB ObjectId string
            
        Returns:
            Order model object with MongoDB id field
            
        Raises:
            HTTPException: If cart is empty or products are unavailable
        """
        # Get user's cart
        cart = await self.cart_repository.find_by_user_id(user_id)
        if not cart or not cart.items:
            raise HTTPException(400, "Cart is empty")

        order_items: list[OrderItem] = []
        total = 0.0

        # Process each cart item (cart now stores integer product_id)
        for cart_item in cart.items:
            # Look up product by integer product_id
            product = await self.product_repository.find_by_product_id(cart_item.product_id)

            # Validate product availability
            if not product or not product.is_active:
                raise HTTPException(400, f"Item unavailable: product_id {cart_item.product_id}")

            # Calculate line total
            line_total = product.price * cart_item.qty
            total += line_total

            # Create order item with MongoDB ObjectId string
            order_items.append(OrderItem(
                product_id=str(product.id),
                name=product.name,
                unit_price=product.price,
                qty=cart_item.qty,
                line_total=line_total
            ))

        # Create order
        order = Order(user_id=user_id, items=order_items, total=total)
        await self.order_repository.create(order)

        # Clear cart after successful order creation
        await self.cart_repository.clear_cart(user_id)

        return order
