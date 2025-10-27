"""Unit tests for CartService business logic."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException

from app.services.cart_service import CartService
from app.db.models.cart import CartItem


class TestCartService:
    """Test suite for CartService."""

    @pytest.mark.asyncio
    @patch('app.services.cart_service.Cart')
    async def test_get_or_create_cart_existing(self, mock_cart_model, mock_cart):
        """Test getting existing cart."""
        # Setup
        mock_cart_model.find_one = AsyncMock(return_value=mock_cart)

        # Execute
        result = await CartService.get_or_create_cart("507f1f77bcf86cd799439012")

        # Assert
        assert result == mock_cart
        mock_cart_model.find_one.assert_called_once()

    @pytest.mark.asyncio
    @patch('app.services.cart_service.Cart')
    async def test_get_or_create_cart_new(self, mock_cart_model):
        """Test creating new cart when none exists."""
        # Setup
        mock_cart_model.find_one = AsyncMock(return_value=None)
        mock_cart_instance = MagicMock()
        mock_cart_instance.insert = AsyncMock()
        mock_cart_model.return_value = mock_cart_instance

        # Execute
        result = await CartService.get_or_create_cart("507f1f77bcf86cd799439012")

        # Assert
        assert result == mock_cart_instance
        mock_cart_instance.insert.assert_called_once()

    @pytest.mark.asyncio
    @patch('app.services.cart_service.Product')
    @patch('app.services.cart_service.Cart')
    async def test_add_item_to_cart_new_item(self, mock_cart_model, mock_product_model, mock_product, mock_empty_cart):
        """Test adding a new item to cart."""
        # Setup
        mock_product_model.get = AsyncMock(return_value=mock_product)
        mock_cart_model.find_one = AsyncMock(return_value=mock_empty_cart)

        # Execute
        result = await CartService.add_item_to_cart("507f1f77bcf86cd799439012", "507f1f77bcf86cd799439011", 2)

        # Assert
        assert len(result.items) == 1
        assert result.items[0].product_id == "507f1f77bcf86cd799439011"
        assert result.items[0].qty == 2
        mock_empty_cart.save.assert_called_once()

    @pytest.mark.asyncio
    @patch('app.services.cart_service.Product')
    @patch('app.services.cart_service.Cart')
    async def test_add_item_to_cart_existing_item(self, mock_cart_model, mock_product_model, mock_product, mock_cart):
        """Test adding quantity to existing item in cart."""
        # Setup
        mock_product_model.get = AsyncMock(return_value=mock_product)
        mock_cart.items[0].product_id = "507f1f77bcf86cd799439011"
        mock_cart.items[0].qty = 2
        mock_cart_model.find_one = AsyncMock(return_value=mock_cart)

        # Execute
        result = await CartService.add_item_to_cart("507f1f77bcf86cd799439012", "507f1f77bcf86cd799439011", 3)

        # Assert
        assert result.items[0].qty == 5  # 2 + 3
        mock_cart.save.assert_called_once()

    @pytest.mark.asyncio
    @patch('app.services.cart_service.Product')
    async def test_add_item_to_cart_product_not_found(self, mock_product_model):
        """Test adding non-existent product to cart."""
        # Setup
        mock_product_model.get = AsyncMock(return_value=None)

        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            await CartService.add_item_to_cart("507f1f77bcf86cd799439012", "invalid_product", 2)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Product not available"

    @pytest.mark.asyncio
    @patch('app.services.cart_service.Product')
    async def test_add_item_to_cart_inactive_product(self, mock_product_model, mock_product):
        """Test adding inactive product to cart."""
        # Setup
        mock_product.is_active = False
        mock_product_model.get = AsyncMock(return_value=mock_product)

        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            await CartService.add_item_to_cart("507f1f77bcf86cd799439012", "507f1f77bcf86cd799439011", 2)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Product not available"

    @pytest.mark.asyncio
    @patch('app.services.cart_service.Product')
    async def test_add_item_to_cart_invalid_quantity(self, mock_product_model, mock_product):
        """Test adding item with invalid quantity."""
        # Setup
        mock_product_model.get = AsyncMock(return_value=mock_product)

        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            await CartService.add_item_to_cart("507f1f77bcf86cd799439012", "507f1f77bcf86cd799439011", 0)

        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Quantity must be greater than 0"

    @pytest.mark.asyncio
    @patch('app.services.cart_service.Product')
    async def test_add_item_to_cart_negative_quantity(self, mock_product_model, mock_product):
        """Test adding item with negative quantity."""
        # Setup
        mock_product_model.get = AsyncMock(return_value=mock_product)

        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            await CartService.add_item_to_cart("507f1f77bcf86cd799439012", "507f1f77bcf86cd799439011", -1)

        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Quantity must be greater than 0"

    @pytest.mark.asyncio
    @patch('app.services.cart_service.Cart')
    async def test_remove_item_from_cart_success(self, mock_cart_model, mock_cart):
        """Test successfully removing item from cart."""
        # Setup
        mock_cart.items = [
            CartItem(product_id="507f1f77bcf86cd799439011", qty=2),
            CartItem(product_id="507f1f77bcf86cd799439099", qty=1)
        ]
        mock_cart_model.find_one = AsyncMock(return_value=mock_cart)

        # Execute
        result = await CartService.remove_item_from_cart("507f1f77bcf86cd799439012", "507f1f77bcf86cd799439011")

        # Assert
        assert len(result.items) == 1
        assert result.items[0].product_id == "507f1f77bcf86cd799439099"
        mock_cart.save.assert_called_once()

    @pytest.mark.asyncio
    @patch('app.services.cart_service.Cart')
    async def test_remove_item_from_cart_not_found(self, mock_cart_model):
        """Test removing item from non-existent cart."""
        # Setup
        mock_cart_model.find_one = AsyncMock(return_value=None)

        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            await CartService.remove_item_from_cart("507f1f77bcf86cd799439012", "507f1f77bcf86cd799439011")

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Cart not found"

    @pytest.mark.asyncio
    @patch('app.services.cart_service.Cart')
    async def test_remove_item_from_cart_item_not_in_cart(self, mock_cart_model, mock_cart):
        """Test removing item that's not in cart."""
        # Setup
        mock_cart.items = [
            CartItem(product_id="507f1f77bcf86cd799439099", qty=1)
        ]
        mock_cart_model.find_one = AsyncMock(return_value=mock_cart)

        # Execute
        result = await CartService.remove_item_from_cart("507f1f77bcf86cd799439012", "507f1f77bcf86cd799439011")

        # Assert - should still succeed but no change
        assert len(result.items) == 1
        assert result.items[0].product_id == "507f1f77bcf86cd799439099"
        mock_cart.save.assert_called_once()

    @pytest.mark.asyncio
    @patch('app.services.cart_service.Cart')
    async def test_clear_cart_success(self, mock_cart_model, mock_cart):
        """Test successfully clearing cart."""
        # Setup
        mock_cart.items = [
            CartItem(product_id="507f1f77bcf86cd799439011", qty=2),
            CartItem(product_id="507f1f77bcf86cd799439099", qty=1)
        ]
        mock_cart_model.find_one = AsyncMock(return_value=mock_cart)

        # Execute
        result = await CartService.clear_cart("507f1f77bcf86cd799439012")

        # Assert
        assert len(result.items) == 0
        mock_cart.save.assert_called_once()

    @pytest.mark.asyncio
    @patch('app.services.cart_service.Cart')
    async def test_clear_cart_no_cart(self, mock_cart_model):
        """Test clearing cart when no cart exists."""
        # Setup
        mock_cart_model.find_one = AsyncMock(return_value=None)

        # Execute
        result = await CartService.clear_cart("507f1f77bcf86cd799439012")

        # Assert - should return None without error
        assert result is None

