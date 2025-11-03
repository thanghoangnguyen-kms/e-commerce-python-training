from fastapi import APIRouter, Depends
from app.api.deps import get_current_user
from app.api.service_deps import get_cart_service
from app.services.cart_service import CartService
from app.schemas.cart import CartItemRequest, CartRemoveRequest

router = APIRouter()

@router.get("")
async def get_cart(user=Depends(get_current_user), cart_service: CartService = Depends(get_cart_service)):
    """
    Get the current user's shopping cart.

    Returns cart with all items or creates a new empty cart if none exists.
    """
    return await cart_service.get_or_create_cart(user["sub"])

@router.post("/add")
async def add_item(data: CartItemRequest, user=Depends(get_current_user), cart_service: CartService = Depends(get_cart_service)):
    """
    Add an item to the shopping cart.

    If the item already exists in the cart, the quantity will be incremented.
    """
    return await cart_service.add_item_to_cart(user["sub"], data.product_id, data.qty)

@router.post("/remove")
async def remove_item(data: CartRemoveRequest, user=Depends(get_current_user), cart_service: CartService = Depends(get_cart_service)):
    """
    Remove an item from the shopping cart.

    Completely removes the item regardless of quantity.
    """
    return await cart_service.remove_item_from_cart(user["sub"], data.product_id)
