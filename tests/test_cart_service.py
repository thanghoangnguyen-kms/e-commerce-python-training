"""
Unit tests for CartService.

- Get or create cart
- Add items (new item, increment existing, validations)
- Remove items
- Clear cart
"""
import pytest
from unittest.mock import AsyncMock, patch
from fastapi import HTTPException

from app.services.cart_service import CartService


class TestCartService:
    """Test cases for cart operations"""

    @pytest.mark.asyncio
    async def test_get_or_create_cart_returns_existing(self, mock_cart_factory):
        """Should return existing cart"""
        # Arrange
        cart = mock_cart_factory(user_id="user_123")

        with patch("app.services.cart_service.Cart") as MockCart:
            MockCart.find_one = AsyncMock(return_value=cart)

            # Act
            result = await CartService.get_or_create_cart("user_123")

            # Assert
            assert result == cart
            cart.insert.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_get_or_create_cart_creates_new(self, mock_cart_factory):
        """Should create new cart when none exists"""
        # Arrange
        new_cart = mock_cart_factory(items=[])

        with patch("app.services.cart_service.Cart") as MockCart:
            MockCart.find_one = AsyncMock(return_value=None)
            MockCart.return_value = new_cart

            # Act
            result = await CartService.get_or_create_cart("user_123")

            # Assert
            assert result == new_cart
            new_cart.insert.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_add_item_to_cart_success(self, mock_cart_factory, mock_product_factory):
        """Should add new item to cart"""
        # Arrange
        product = mock_product_factory(id="prod_1", is_active=True)
        cart = mock_cart_factory(items=[])

        with patch("app.services.cart_service.Product") as MockProduct, \
             patch("app.services.cart_service.CartService.get_or_create_cart", AsyncMock(return_value=cart)):

            MockProduct.get = AsyncMock(return_value=product)

            # Act
            result = await CartService.add_item_to_cart("user_1", "prod_1", 2)

            # Assert
            assert len(result.items) == 1
            assert result.items[0].product_id == "prod_1"
            assert result.items[0].qty == 2
            cart.save.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_add_item_increments_existing_quantity(
        self, mock_cart_factory, mock_product_factory, mock_cart_item_factory
    ):
        """Should increment quantity for existing item"""
        # Arrange
        existing_item = mock_cart_item_factory(product_id="prod_1", qty=1)
        cart = mock_cart_factory(items=[existing_item])
        product = mock_product_factory(id="prod_1", is_active=True)

        with patch("app.services.cart_service.Product") as MockProduct, \
             patch("app.services.cart_service.CartService.get_or_create_cart", AsyncMock(return_value=cart)):

            MockProduct.get = AsyncMock(return_value=product)

            # Act
            result = await CartService.add_item_to_cart("user_1", "prod_1", 2)

            # Assert
            assert len(result.items) == 1
            assert result.items[0].qty == 3  # 1 + 2

    @pytest.mark.asyncio
    async def test_add_item_fails_invalid_quantity(self, mock_product_factory):
        """Should raise 400 for invalid quantity"""
        # Arrange
        product = mock_product_factory(is_active=True)

        with patch("app.services.cart_service.Product") as MockProduct:
            MockProduct.get = AsyncMock(return_value=product)

            # Act & Assert
            with pytest.raises(HTTPException) as exc:
                await CartService.add_item_to_cart("user_1", "prod_1", 0)

            assert exc.value.status_code == 400

    @pytest.mark.asyncio
    async def test_add_item_fails_product_not_available(self):
        """Should raise 404 when product not found or inactive"""
        # Arrange
        with patch("app.services.cart_service.Product") as MockProduct:
            MockProduct.get = AsyncMock(return_value=None)

            # Act & Assert
            with pytest.raises(HTTPException) as exc:
                await CartService.add_item_to_cart("user_1", "prod_1", 1)

            assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_remove_item_from_cart(self, mock_cart_factory, mock_cart_item_factory):
        """Should remove specified item"""
        # Arrange
        item1 = mock_cart_item_factory(product_id="prod_1")
        item2 = mock_cart_item_factory(product_id="prod_2")
        cart = mock_cart_factory(items=[item1, item2])

        with patch("app.services.cart_service.Cart") as MockCart:
            MockCart.find_one = AsyncMock(return_value=cart)

            # Act
            result = await CartService.remove_item_from_cart("user_1", "prod_1")

            # Assert
            assert len(result.items) == 1
            assert result.items[0].product_id == "prod_2"

    @pytest.mark.asyncio
    async def test_clear_cart(self, mock_cart_factory, mock_cart_item_factory):
        """Should clear all items"""
        # Arrange
        items = [mock_cart_item_factory(), mock_cart_item_factory()]
        cart = mock_cart_factory(items=items)

        with patch("app.services.cart_service.Cart") as MockCart:
            MockCart.find_one = AsyncMock(return_value=cart)

            # Act
            result = await CartService.clear_cart("user_1")

            # Assert
            assert result.items == []
            cart.save.assert_awaited_once()


