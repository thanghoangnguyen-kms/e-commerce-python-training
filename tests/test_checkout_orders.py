"""Unit tests for CheckoutService business logic."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException

from app.services.checkout_service import CheckoutService
from app.db.models.cart import CartItem
from app.db.models.order import OrderItem


class TestCheckoutService:
    """Test suite for CheckoutService."""

    @pytest.mark.asyncio
    @patch('app.services.checkout_service.Order')
    @patch('app.services.checkout_service.Product')
    @patch('app.services.checkout_service.Cart')
    async def test_create_order_from_cart_success(self, mock_cart_model, mock_product_model, mock_order_model, mock_cart, mock_product):
        """Test successfully creating order from cart."""
        # Setup
        mock_cart.items = [
            CartItem(product_id="507f1f77bcf86cd799439011", qty=2)
        ]
        mock_cart_model.find_one = AsyncMock(return_value=mock_cart)

        mock_product.id = "507f1f77bcf86cd799439011"
        mock_product.name = "Test Product"
        mock_product.price = 99.99
        mock_product.is_active = True
        mock_product_model.get = AsyncMock(return_value=mock_product)

        mock_order_instance = MagicMock()
        mock_order_instance.insert = AsyncMock()
        mock_order_model.return_value = mock_order_instance

        # Execute
        result = await CheckoutService.create_order_from_cart("507f1f77bcf86cd799439012")

        # Assert
        assert result == mock_order_instance
        mock_order_instance.insert.assert_called_once()
        mock_cart.save.assert_called_once()
        assert len(mock_cart.items) == 0  # Cart should be cleared

    @pytest.mark.asyncio
    @patch('app.services.checkout_service.Cart')
    async def test_create_order_from_cart_empty_cart(self, mock_cart_model, mock_empty_cart):
        """Test creating order from empty cart."""
        # Setup
        mock_cart_model.find_one = AsyncMock(return_value=mock_empty_cart)

        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            await CheckoutService.create_order_from_cart("507f1f77bcf86cd799439012")

        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Cart is empty"

    @pytest.mark.asyncio
    @patch('app.services.checkout_service.Cart')
    async def test_create_order_from_cart_no_cart(self, mock_cart_model):
        """Test creating order when cart doesn't exist."""
        # Setup
        mock_cart_model.find_one = AsyncMock(return_value=None)

        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            await CheckoutService.create_order_from_cart("507f1f77bcf86cd799439012")

        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Cart is empty"

    @pytest.mark.asyncio
    @patch('app.services.checkout_service.Product')
    @patch('app.services.checkout_service.Cart')
    async def test_create_order_from_cart_product_not_found(self, mock_cart_model, mock_product_model, mock_cart):
        """Test creating order when product no longer exists."""
        # Setup
        mock_cart.items = [
            CartItem(product_id="507f1f77bcf86cd799439011", qty=2)
        ]
        mock_cart_model.find_one = AsyncMock(return_value=mock_cart)
        mock_product_model.get = AsyncMock(return_value=None)

        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            await CheckoutService.create_order_from_cart("507f1f77bcf86cd799439012")

        assert exc_info.value.status_code == 400
        assert "Item unavailable" in exc_info.value.detail

    @pytest.mark.asyncio
    @patch('app.services.checkout_service.Product')
    @patch('app.services.checkout_service.Cart')
    async def test_create_order_from_cart_product_inactive(self, mock_cart_model, mock_product_model, mock_cart, mock_product):
        """Test creating order when product is inactive."""
        # Setup
        mock_cart.items = [
            CartItem(product_id="507f1f77bcf86cd799439011", qty=2)
        ]
        mock_cart_model.find_one = AsyncMock(return_value=mock_cart)

        mock_product.is_active = False
        mock_product_model.get = AsyncMock(return_value=mock_product)

        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            await CheckoutService.create_order_from_cart("507f1f77bcf86cd799439012")

        assert exc_info.value.status_code == 400
        assert "Item unavailable" in exc_info.value.detail

    @pytest.mark.asyncio
    @patch('app.services.checkout_service.Order')
    @patch('app.services.checkout_service.Product')
    @patch('app.services.checkout_service.Cart')
    async def test_create_order_from_cart_multiple_items(self, mock_cart_model, mock_product_model, mock_order_model, mock_cart):
        """Test creating order from cart with multiple items."""
        # Setup
        mock_cart.items = [
            CartItem(product_id="507f1f77bcf86cd799439011", qty=2),
            CartItem(product_id="507f1f77bcf86cd799439022", qty=1)
        ]
        mock_cart_model.find_one = AsyncMock(return_value=mock_cart)

        # Mock two different products
        product1 = MagicMock()
        product1.id = "507f1f77bcf86cd799439011"
        product1.name = "Product 1"
        product1.price = 99.99
        product1.is_active = True

        product2 = MagicMock()
        product2.id = "507f1f77bcf86cd799439022"
        product2.name = "Product 2"
        product2.price = 49.99
        product2.is_active = True

        mock_product_model.get = AsyncMock(side_effect=[product1, product2])

        mock_order_instance = MagicMock()
        mock_order_instance.insert = AsyncMock()
        mock_order_model.return_value = mock_order_instance

        # Execute
        result = await CheckoutService.create_order_from_cart("507f1f77bcf86cd799439012")

        # Assert
        assert result == mock_order_instance
        mock_order_instance.insert.assert_called_once()

        # Verify order was created with correct parameters
        call_args = mock_order_model.call_args
        assert call_args.kwargs['user_id'] == "507f1f77bcf86cd799439012"
        assert len(call_args.kwargs['items']) == 2
        assert call_args.kwargs['total'] == 249.97  # (99.99 * 2) + (49.99 * 1)

    @pytest.mark.asyncio
    @patch('app.services.checkout_service.Order')
    @patch('app.services.checkout_service.Product')
    @patch('app.services.checkout_service.Cart')
    async def test_create_order_from_cart_calculates_totals_correctly(self, mock_cart_model, mock_product_model, mock_order_model, mock_cart):
        """Test that order totals are calculated correctly."""
        # Setup
        mock_cart.items = [
            CartItem(product_id="507f1f77bcf86cd799439011", qty=3)
        ]
        mock_cart_model.find_one = AsyncMock(return_value=mock_cart)

        mock_product = MagicMock()
        mock_product.id = "507f1f77bcf86cd799439011"
        mock_product.name = "Test Product"
        mock_product.price = 25.50
        mock_product.is_active = True
        mock_product_model.get = AsyncMock(return_value=mock_product)

        mock_order_instance = MagicMock()
        mock_order_instance.insert = AsyncMock()
        mock_order_model.return_value = mock_order_instance

        # Execute
        await CheckoutService.create_order_from_cart("507f1f77bcf86cd799439012")

        # Assert
        call_args = mock_order_model.call_args
        assert call_args.kwargs['total'] == 76.50  # 25.50 * 3
        assert call_args.kwargs['items'][0].line_total == 76.50
        assert call_args.kwargs['items'][0].unit_price == 25.50
        assert call_args.kwargs['items'][0].qty == 3

