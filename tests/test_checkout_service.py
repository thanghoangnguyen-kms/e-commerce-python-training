"""
Unit tests for CheckoutService.

- Create order from cart (success, total calculation)
- Validation (empty cart, product issues)
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from fastapi import HTTPException

from app.services.checkout_service import CheckoutService
from app.repositories.cart_repository import CartRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.order_repository import OrderRepository


class TestCheckoutService:
    """Test cases for checkout operations"""

    @pytest.mark.asyncio
    async def test_create_order_from_cart_success(
        self, mock_cart_factory, mock_product_factory, mock_order_factory, mock_cart_item_factory
    ):
        """Should create order and clear cart"""
        # Arrange
        product = mock_product_factory(id="prod_1", product_id=1, name="Test", price=50.0, is_active=True)
        cart_item = mock_cart_item_factory(product_id=1, qty=2)  # Changed to integer
        cart = mock_cart_factory(items=[cart_item])
        order = mock_order_factory(user_id="user_1", total=100.0)
        
        mock_cart_repo = Mock(spec=CartRepository)
        mock_cart_repo.find_by_user_id = AsyncMock(return_value=cart)
        mock_cart_repo.clear_cart = AsyncMock(return_value=cart)
        
        mock_product_repo = Mock(spec=ProductRepository)
        mock_product_repo.find_by_product_id = AsyncMock(return_value=product)  # Changed to find_by_product_id
        
        mock_order_repo = Mock(spec=OrderRepository)
        mock_order_repo.create = AsyncMock(return_value=order)
        
        service = CheckoutService(
            cart_repository=mock_cart_repo,
            product_repository=mock_product_repo,
            order_repository=mock_order_repo
        )

        # Mock Order model constructor
        with patch("app.services.checkout_service.Order", return_value=order):
            # Act
            result = await service.create_order_from_cart("user_1")

        # Assert
        assert result == order
        mock_order_repo.create.assert_called_once()
        mock_cart_repo.clear_cart.assert_called_once_with("user_1")

    @pytest.mark.asyncio
    async def test_create_order_calculates_total(
        self, mock_cart_factory, mock_product_factory, mock_order_factory, mock_cart_item_factory
    ):
        """Should calculate correct total from multiple items"""
        # Arrange
        prod1 = mock_product_factory(id="p1", product_id=1, price=25.0, is_active=True)
        prod2 = mock_product_factory(id="p2", product_id=2, price=50.0, is_active=True)

        items = [
            mock_cart_item_factory(product_id=1, qty=2),  # 50
            mock_cart_item_factory(product_id=2, qty=1),  # 50
        ]
        cart = mock_cart_factory(items=items)
        order = mock_order_factory()
        
        mock_cart_repo = Mock(spec=CartRepository)
        mock_cart_repo.find_by_user_id = AsyncMock(return_value=cart)
        mock_cart_repo.clear_cart = AsyncMock(return_value=cart)
        
        mock_product_repo = Mock(spec=ProductRepository)
        mock_product_repo.find_by_product_id = AsyncMock(side_effect=[prod1, prod2])  # Changed to find_by_product_id
        
        mock_order_repo = Mock(spec=OrderRepository)
        mock_order_repo.create = AsyncMock(return_value=order)
        
        service = CheckoutService(
            cart_repository=mock_cart_repo,
            product_repository=mock_product_repo,
            order_repository=mock_order_repo
        )

        # Mock Order model constructor
        with patch("app.services.checkout_service.Order", return_value=order):
            # Act
            await service.create_order_from_cart("user_1")

        # Assert - total should be 100.0
        mock_order_repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_order_fails_empty_cart(self):
        """Should raise 400 when cart is empty"""
        # Arrange
        mock_cart_repo = Mock(spec=CartRepository)
        mock_cart_repo.find_by_user_id = AsyncMock(return_value=None)
        
        service = CheckoutService(cart_repository=mock_cart_repo)

        # Act & Assert
        with pytest.raises(HTTPException) as exc:
            await service.create_order_from_cart("user_1")

        assert exc.value.status_code == 400

    @pytest.mark.asyncio
    async def test_create_order_fails_product_not_found(
        self, mock_cart_factory, mock_cart_item_factory
    ):
        """Should raise 400 when product doesn't exist"""
        # Arrange
        cart_item = mock_cart_item_factory(product_id=999)  # Changed to integer
        cart = mock_cart_factory(items=[cart_item])

        mock_product_repo = Mock(spec=ProductRepository)
        mock_product_repo.find_by_product_id = AsyncMock(return_value=None)  # Changed

        mock_cart_repo = Mock(spec=CartRepository)
        mock_cart_repo.find_by_user_id = AsyncMock(return_value=cart)

        service = CheckoutService(
            cart_repository=mock_cart_repo,
            product_repository=mock_product_repo
        )

        # Act & Assert
        with pytest.raises(HTTPException) as exc:
            await service.create_order_from_cart("user_1")

        assert exc.value.status_code == 400
        assert "unavailable" in str(exc.value.detail).lower()

    @pytest.mark.asyncio
    async def test_create_order_fails_product_inactive(
        self, mock_cart_factory, mock_product_factory, mock_cart_item_factory
    ):
        """Should raise 400 when product is inactive"""
        # Arrange
        product = mock_product_factory(id="prod_1", product_id=1, is_active=False)
        cart_item = mock_cart_item_factory(product_id=1)
        cart = mock_cart_factory(items=[cart_item])

        mock_product_repo = Mock(spec=ProductRepository)
        mock_product_repo.find_by_product_id = AsyncMock(return_value=product)

        mock_cart_repo = Mock(spec=CartRepository)
        mock_cart_repo.find_by_user_id = AsyncMock(return_value=cart)

        service = CheckoutService(
            cart_repository=mock_cart_repo,
            product_repository=mock_product_repo
        )

        # Act & Assert
        with pytest.raises(HTTPException) as exc:
            await service.create_order_from_cart("user_1")

        assert exc.value.status_code == 400
        assert "unavailable" in str(exc.value.detail).lower()
