from app.db.models.cart import Cart
from app.repositories.cart_repository import CartRepository
from app.repositories.product_repository import ProductRepository
from app.core.service_decorator import service_method
from fastapi import HTTPException


class CartService:
    """
    Service layer for cart operations.
    Handles all business logic related to shopping cart management.
    """

    def __init__(
        self, 
        cart_repository: CartRepository = None, 
        product_repository: ProductRepository = None
    ):
        """Initialize CartService with repository dependencies."""
        self.cart_repository = cart_repository or CartRepository()
        self.product_repository = product_repository or ProductRepository()

    @service_method
    async def get_or_create_cart(self, user_id: str) -> Cart:
        """Get user's cart or create a new one if it doesn't exist."""
        return await self.cart_repository.get_or_create_cart(user_id)

    @service_method
    async def add_item_to_cart(self, user_id: str, product_id: int, qty: int) -> Cart:
        """
        Add an item to the user's cart.
        If item already exists, increment quantity.
        Stores integer product_id in cart for easy reference.
        """
        # Validate product exists and is active using product_id (integer)
        product = await self.product_repository.find_by_product_id(product_id)
        if not product or not product.is_active:
            raise HTTPException(404, "Product not available")

        if qty <= 0:
            raise HTTPException(400, "Quantity must be greater than 0")

        # Add item to cart using the integer product_id (not MongoDB ObjectId)
        cart = await self.cart_repository.add_item(user_id, product_id, qty)
        return cart

    @service_method
    async def remove_item_from_cart(self, user_id: str, product_id: int) -> Cart:
        """
        Remove an item completely from the user's cart.
        Uses integer product_id for lookup and removal.
        """
        # Validate product exists
        product = await self.product_repository.find_by_product_id(product_id)
        if not product:
            raise HTTPException(404, "Product not found")
        
        cart = await self.cart_repository.remove_item(user_id, product_id)
        if not cart:
            raise HTTPException(404, "Cart not found")
        return cart

    @service_method
    async def clear_cart(self, user_id: str) -> Cart:
        """Clear all items from the user's cart."""
        cart = await self.cart_repository.clear_cart(user_id)
        if not cart:
            raise HTTPException(404, "Cart not found")
        return cart
