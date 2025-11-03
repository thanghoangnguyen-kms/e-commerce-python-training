"""
Cart repository for cart-related data access operations.
"""
from app.repositories.base_repository import BaseRepository
from app.db.models.cart import Cart, CartItem


class CartRepository(BaseRepository[Cart]):
    """Repository for Cart model operations."""

    def __init__(self):
        super().__init__(Cart)

    async def find_by_user_id(self, user_id: str) -> Cart | None:
        """Find a cart by user ID."""
        return await self.find_one(Cart.user_id == user_id)

    async def get_or_create_cart(self, user_id: str) -> Cart:
        """Get user's cart or create a new one if it doesn't exist."""
        cart = await self.find_by_user_id(user_id)
        if not cart:
            cart = Cart(user_id=user_id, items=[])
            await self.create(cart)
        return cart

    async def add_item(self, user_id: str, product_id: int, quantity: int) -> Cart:
        """Add an item to the cart or update quantity if it exists."""
        cart = await self.get_or_create_cart(user_id)
        
        # Check if item already exists
        item_found = False
        for item in cart.items:
            if item.product_id == product_id:
                item.qty += quantity
                item_found = True
                break
        
        # If not found, add new item
        if not item_found:
            cart.items.append(CartItem(product_id=product_id, qty=quantity))
        
        await self.update(cart)
        return cart

    async def remove_item(self, user_id: str, product_id: int) -> Cart | None:
        """Remove an item from the cart."""
        cart = await self.find_by_user_id(user_id)
        if cart:
            cart.items = [item for item in cart.items if item.product_id != product_id]
            await self.update(cart)
        return cart

    async def clear_cart(self, user_id: str) -> Cart | None:
        """Clear all items from the cart."""
        cart = await self.find_by_user_id(user_id)
        if cart:
            cart.items = []
            await self.update(cart)
        return cart
