"""
Unit tests for CheckoutService.

- Create order from cart (success, total calculation)
- Validation (empty cart, product issues)
"""
import pytest
from unittest.mock import AsyncMock, patch
from fastapi import HTTPException

from app.services.checkout_service import CheckoutService


class TestCheckoutService:
    """Test cases for checkout operations"""

    @pytest.mark.asyncio
    async def test_create_order_from_cart_success(
        self, mock_cart_factory, mock_product_factory, mock_order_factory, mock_cart_item_factory
    ):
        """Should create order and clear cart"""
        # Arrange
        product = mock_product_factory(id="prod_1", name="Test", price=50.0, is_active=True)
        cart_item = mock_cart_item_factory(product_id="prod_1", qty=2)
        cart = mock_cart_factory(user_id="user_1", items=[cart_item])
        order = mock_order_factory(user_id="user_1", total=100.0)

        with patch("app.services.checkout_service.Cart") as MockCart, \
             patch("app.services.checkout_service.Product") as MockProduct, \
             patch("app.services.checkout_service.Order") as MockOrder:

            MockCart.find_one = AsyncMock(return_value=cart)
            MockProduct.get = AsyncMock(return_value=product)
            MockOrder.return_value = order

            # Act
            result = await CheckoutService.create_order_from_cart("user_1")

            # Assert
            assert result == order
            order.insert.assert_awaited_once()
            assert cart.items == []  # Cart cleared
            cart.save.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_create_order_calculates_total(
        self, mock_cart_factory, mock_product_factory, mock_order_factory, mock_cart_item_factory
    ):
        """Should calculate correct total from multiple items"""
        # Arrange
        prod1 = mock_product_factory(id="p1", price=25.0, is_active=True)
        prod2 = mock_product_factory(id="p2", price=50.0, is_active=True)

        items = [
            mock_cart_item_factory(product_id="p1", qty=2),  # 50
            mock_cart_item_factory(product_id="p2", qty=1),  # 50
        ]
        cart = mock_cart_factory(items=items)
        order = mock_order_factory()

        with patch("app.services.checkout_service.Cart") as MockCart, \
             patch("app.services.checkout_service.Product") as MockProduct, \
             patch("app.services.checkout_service.Order") as MockOrder:

            MockCart.find_one = AsyncMock(return_value=cart)
            MockProduct.get = AsyncMock(side_effect=[prod1, prod2])
            MockOrder.return_value = order

            # Act
            await CheckoutService.create_order_from_cart("user_1")

            # Assert - total should be 100.0
            order.insert.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_create_order_fails_empty_cart(self):
        """Should raise 400 when cart is empty"""
        # Arrange
        with patch("app.services.checkout_service.Cart") as MockCart:
            MockCart.find_one = AsyncMock(return_value=None)

            # Act & Assert
            with pytest.raises(HTTPException) as exc:
                await CheckoutService.create_order_from_cart("user_1")

            assert exc.value.status_code == 400

    @pytest.mark.asyncio
    async def test_create_order_fails_product_not_found(
        self, mock_cart_factory, mock_cart_item_factory
    ):
        """Should raise 400 when product doesn't exist"""
        # Arrange
        cart_item = mock_cart_item_factory(product_id="nonexistent")
        cart = mock_cart_factory(items=[cart_item])

        with patch("app.services.checkout_service.Cart") as MockCart, \
             patch("app.services.checkout_service.Product") as MockProduct:

            MockCart.find_one = AsyncMock(return_value=cart)
            MockProduct.get = AsyncMock(return_value=None)

            # Act & Assert
            with pytest.raises(HTTPException) as exc:
                await CheckoutService.create_order_from_cart("user_1")

            assert exc.value.status_code == 400

    @pytest.mark.asyncio
    async def test_create_order_fails_product_inactive(
        self, mock_cart_factory, mock_product_factory, mock_cart_item_factory
    ):
        """Should raise 400 when product is inactive"""
        # Arrange
        product = mock_product_factory(id="prod_1", is_active=False)
        cart_item = mock_cart_item_factory(product_id="prod_1")
        cart = mock_cart_factory(items=[cart_item])

        with patch("app.services.checkout_service.Cart") as MockCart, \
             patch("app.services.checkout_service.Product") as MockProduct:

            MockCart.find_one = AsyncMock(return_value=cart)
            MockProduct.get = AsyncMock(return_value=product)

            # Act & Assert
            with pytest.raises(HTTPException) as exc:
                await CheckoutService.create_order_from_cart("user_1")

            assert exc.value.status_code == 400


