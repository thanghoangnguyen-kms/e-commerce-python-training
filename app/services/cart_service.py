from app.db.models.cart import Cart, CartItem
from app.db.models.product import Product
from fastapi import HTTPException


class CartService:
    """
    Service layer for cart operations.
    Handles all business logic related to shopping cart management.
    """

    @staticmethod
    async def get_or_create_cart(user_id: str) -> Cart:
        """Get user's cart or create a new one if it doesn't exist."""
        cart = await Cart.find_one(Cart.user_id == user_id)
        if not cart:
            cart = Cart(user_id=user_id, items=[])
            await cart.insert()
        return cart

    @staticmethod
    async def add_item_to_cart(user_id: str, product_id: str, qty: int) -> Cart:
        """
        Add an item to the user's cart.
        If item already exists, increment quantity.
        """
        # Validate product exists and is active
        product = await Product.get(product_id)
        if not product or not product.is_active:
            raise HTTPException(404, "Product not available")

        if qty <= 0:
            raise HTTPException(400, "Quantity must be greater than 0")

        # Get or create cart
        cart = await CartService.get_or_create_cart(user_id)

        # Check if item already in cart
        item_found = False
        for item in cart.items:
            if item.product_id == product_id:
                item.qty += qty
                item_found = True
                break

        # If not found, add new item
        if not item_found:
            cart.items.append(CartItem(product_id=product_id, qty=qty))

        await cart.save()
        return cart

    @staticmethod
    async def remove_item_from_cart(user_id: str, product_id: str) -> Cart:
        """Remove an item completely from the user's cart."""
        cart = await Cart.find_one(Cart.user_id == user_id)
        if not cart:
            raise HTTPException(404, "Cart not found")

        cart.items = [item for item in cart.items if item.product_id != product_id]
        await cart.save()
        return cart

    @staticmethod
    async def clear_cart(user_id: str) -> Cart:
        """Clear all items from the user's cart."""
        cart = await Cart.find_one(Cart.user_id == user_id)
        if cart:
            cart.items = []
            await cart.save()
        return cart

