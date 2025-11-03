"""
Unit tests for OrderService.

- Get user orders
- Get order by ID with authorization
- Get all orders (admin)
"""
import pytest
from unittest.mock import Mock, AsyncMock
from fastapi import HTTPException

from app.services.order_service import OrderService
from app.repositories.order_repository import OrderRepository


class TestOrderService:
    """Test cases for order operations"""

    @pytest.mark.asyncio
    async def test_get_user_orders(self, mock_order_factory):
        """Should return user's orders as Order model objects"""
        # Arrange
        orders = [mock_order_factory(user_id="user_1"), mock_order_factory(user_id="user_1")]

        mock_repo = Mock(spec=OrderRepository)
        mock_repo.find_by_user_id = AsyncMock(return_value=orders)

        service = OrderService(order_repository=mock_repo)

        # Act
        result = await service.get_user_orders("user_1")

        # Assert
        assert len(result) == 2
        assert result[0].user_id == "user_1"
        assert hasattr(result[0], 'id')  # MongoDB id field is included
        mock_repo.find_by_user_id.assert_called_once_with("user_1", 0, 20)

    @pytest.mark.asyncio
    async def test_get_order_by_id_success(self, mock_order_factory):
        """Should return order as Order model object when it belongs to user"""
        # Arrange
        order = mock_order_factory(id="order_1", user_id="user_1")

        mock_repo = Mock(spec=OrderRepository)
        mock_repo.find_by_id_and_user = AsyncMock(return_value=order)

        service = OrderService(order_repository=mock_repo)

        # Act
        result = await service.get_order_by_id("order_1", "user_1")

        # Assert
        assert result.id == "order_1"
        assert result.user_id == "user_1"
        assert hasattr(result, 'id')  # MongoDB id field is included
        mock_repo.find_by_id_and_user.assert_called_once_with("order_1", "user_1")

    @pytest.mark.asyncio
    async def test_get_order_by_id_not_found(self):
        """Should raise 404 when order doesn't exist"""
        # Arrange
        mock_repo = Mock(spec=OrderRepository)
        mock_repo.find_by_id_and_user = AsyncMock(return_value=None)

        service = OrderService(order_repository=mock_repo)

        # Act & Assert
        with pytest.raises(HTTPException) as exc:
            await service.get_order_by_id("order_1", "user_1")

        assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_get_order_by_id_fails_wrong_user(self, mock_order_factory):
        """Should raise 404 when order belongs to different user"""
        # Arrange
        mock_repo = Mock(spec=OrderRepository)
        mock_repo.find_by_id_and_user = AsyncMock(return_value=None)  # Returns None when user doesn't match

        service = OrderService(order_repository=mock_repo)

        # Act & Assert
        with pytest.raises(HTTPException) as exc:
            await service.get_order_by_id("order_1", "user_1")

        assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_get_all_orders(self, mock_order_factory):
        """Should return all orders as Order model objects (admin function)"""
        # Arrange
        orders = [
            mock_order_factory(user_id="user1"),
            mock_order_factory(user_id="user2"),
        ]

        mock_repo = Mock(spec=OrderRepository)
        mock_repo.find_all = AsyncMock(return_value=orders)

        service = OrderService(order_repository=mock_repo)

        # Act
        result = await service.get_all_orders()

        # Assert
        assert len(result) == 2
        assert result[0].user_id == "user1"
        assert hasattr(result[0], 'id')  # MongoDB id field is included
        mock_repo.find_all.assert_called_once()
