"""
Unit tests for CartService.

- Get or create cart
- Add items (new item, increment existing, validations)
- Remove items
- Clear cart
"""
import pytest
from unittest.mock import Mock, AsyncMock
from fastapi import HTTPException

from app.services.cart_service import CartService
from app.repositories.cart_repository import CartRepository
from app.repositories.product_repository import ProductRepository


class TestCartService:
    """Test cases for cart operations"""

    @pytest.mark.asyncio
    async def test_get_or_create_cart_returns_existing(self, mock_cart_factory):
        """Should return existing cart"""
        # Arrange
        cart = mock_cart_factory(user_id="user_123")
        
        mock_cart_repo = Mock(spec=CartRepository)
        mock_cart_repo.get_or_create_cart = AsyncMock(return_value=cart)
        
        service = CartService(cart_repository=mock_cart_repo)

        # Act
        result = await service.get_or_create_cart("user_123")

        # Assert
        assert result == cart
        mock_cart_repo.get_or_create_cart.assert_called_once_with("user_123")

    @pytest.mark.asyncio
    async def test_get_or_create_cart_creates_new(self, mock_cart_factory):
        """Should create new cart when none exists"""
        # Arrange
        new_cart = mock_cart_factory(items=[])
        
        mock_cart_repo = Mock(spec=CartRepository)
        mock_cart_repo.get_or_create_cart = AsyncMock(return_value=new_cart)
        
        service = CartService(cart_repository=mock_cart_repo)

        # Act
        result = await service.get_or_create_cart("user_123")

        # Assert
        assert result == new_cart

    @pytest.mark.asyncio
    async def test_add_item_to_cart_success(self, mock_cart_factory, mock_product_factory):
        """Should add new item to cart"""
        # Arrange
        product = mock_product_factory(id="prod_mongo_id", product_id=1, is_active=True)
        cart = mock_cart_factory(items=[])
        
        mock_product_repo = Mock(spec=ProductRepository)
        mock_product_repo.find_by_product_id = AsyncMock(return_value=product)
        
        mock_cart_repo = Mock(spec=CartRepository)
        mock_cart_repo.add_item = AsyncMock(return_value=cart)
        
        service = CartService(cart_repository=mock_cart_repo, product_repository=mock_product_repo)

        # Act
        result = await service.add_item_to_cart("user_1", 1, 2)

        # Assert
        assert result == cart
        mock_product_repo.find_by_product_id.assert_called_once_with(1)
        mock_cart_repo.add_item.assert_called_once_with("user_1", 1, 2)  # Changed to use integer product_id

    @pytest.mark.asyncio
    async def test_add_item_increments_existing_quantity(
        self, mock_cart_factory, mock_product_factory, mock_cart_item_factory
    ):
        """Should increment quantity for existing cart item"""
        # Arrange
        product = mock_product_factory(id="prod_mongo_id", product_id=1, is_active=True)
        existing_item = mock_cart_item_factory(product_id=1, qty=1)  # Changed to integer product_id
        cart = mock_cart_factory(items=[existing_item])
        
        mock_product_repo = Mock(spec=ProductRepository)
        mock_product_repo.find_by_product_id = AsyncMock(return_value=product)
        
        mock_cart_repo = Mock(spec=CartRepository)
        mock_cart_repo.add_item = AsyncMock(return_value=cart)
        
        service = CartService(cart_repository=mock_cart_repo, product_repository=mock_product_repo)

        # Act
        result = await service.add_item_to_cart("user_1", 1, 2)

        # Assert
        assert result == cart
        mock_product_repo.find_by_product_id.assert_called_once_with(1)

    @pytest.mark.asyncio
    async def test_add_item_fails_invalid_quantity(self, mock_product_factory):
        """Should raise 400 for invalid quantity"""
        # Arrange
        product = mock_product_factory(id="prod_mongo_id", product_id=1, is_active=True)
        
        mock_product_repo = Mock(spec=ProductRepository)
        mock_product_repo.find_by_product_id = AsyncMock(return_value=product)
        
        service = CartService(product_repository=mock_product_repo)

        # Act & Assert
        with pytest.raises(HTTPException) as exc:
            await service.add_item_to_cart("user_1", 1, 0)
        
        assert exc.value.status_code == 400

    @pytest.mark.asyncio
    async def test_add_item_fails_product_not_available(self):
        """Should raise 404 when product doesn't exist or is inactive"""
        # Arrange
        mock_product_repo = Mock(spec=ProductRepository)
        mock_product_repo.find_by_product_id = AsyncMock(return_value=None)
        
        service = CartService(product_repository=mock_product_repo)

        # Act & Assert
        with pytest.raises(HTTPException) as exc:
            await service.add_item_to_cart("user_1", 999, 1)
        
        assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_remove_item_from_cart(self, mock_cart_factory, mock_product_factory):
        """Should remove item from cart"""
        # Arrange
        product = mock_product_factory(id="prod_mongo_id", product_id=1)
        cart = mock_cart_factory(items=[])

        mock_product_repo = Mock(spec=ProductRepository)
        mock_product_repo.find_by_product_id = AsyncMock(return_value=product)

        mock_cart_repo = Mock(spec=CartRepository)
        mock_cart_repo.remove_item = AsyncMock(return_value=cart)

        service = CartService(cart_repository=mock_cart_repo, product_repository=mock_product_repo)

        # Act
        result = await service.remove_item_from_cart("user_1", 1)

        # Assert
        assert result == cart
        mock_product_repo.find_by_product_id.assert_called_once_with(1)
        mock_cart_repo.remove_item.assert_called_once_with("user_1", 1)  # Changed to integer

    @pytest.mark.asyncio
    async def test_clear_cart(self, mock_cart_factory):
        """Should clear all items"""
        # Arrange
        cart = mock_cart_factory(items=[])
        
        mock_cart_repo = Mock(spec=CartRepository)
        mock_cart_repo.clear_cart = AsyncMock(return_value=cart)
        
        service = CartService(cart_repository=mock_cart_repo)

        # Act
        result = await service.clear_cart("user_1")

        # Assert
        assert result.items == []
        mock_cart_repo.clear_cart.assert_called_once_with("user_1")
