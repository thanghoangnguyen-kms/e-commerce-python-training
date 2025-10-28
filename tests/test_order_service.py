"""
Unit tests for OrderService.

- Get user orders
- Get order by ID with authorization
- Get all orders (admin)
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi import HTTPException

from app.services.order_service import OrderService
from tests.conftest import QueryChain


class TestOrderService:
    """Test cases for order operations"""

    @pytest.mark.asyncio
    async def test_get_user_orders(self, mock_order_factory):
        """Should return user's orders"""
        # Arrange
        orders = [mock_order_factory(user_id="user_1"), mock_order_factory(user_id="user_1")]

        with patch("app.services.order_service.Order") as MockOrder:
            MockOrder.find = MagicMock(return_value=QueryChain(orders))

            # Act
            result = await OrderService.get_user_orders("user_1")

            # Assert
            assert len(result) == 2

    @pytest.mark.asyncio
    async def test_get_order_by_id_success(self, mock_order_factory):
        """Should return order when it belongs to user"""
        # Arrange
        order = mock_order_factory(id="order_1", user_id="user_1")

        with patch("app.services.order_service.Order") as MockOrder:
            MockOrder.get = AsyncMock(return_value=order)

            # Act
            result = await OrderService.get_order_by_id("order_1", "user_1")

            # Assert
            assert result == order

    @pytest.mark.asyncio
    async def test_get_order_by_id_not_found(self):
        """Should raise 404 when order doesn't exist"""
        # Arrange
        with patch("app.services.order_service.Order") as MockOrder:
            MockOrder.get = AsyncMock(return_value=None)

            # Act & Assert
            with pytest.raises(HTTPException) as exc:
                await OrderService.get_order_by_id("order_1", "user_1")

            assert exc.value.status_code == 404

    @pytest.mark.asyncio
    async def test_get_order_by_id_fails_wrong_user(self, mock_order_factory):
        """Should raise 403 when order belongs to different user"""
        # Arrange
        order = mock_order_factory(id="order_1", user_id="user_2")

        with patch("app.services.order_service.Order") as MockOrder:
            MockOrder.get = AsyncMock(return_value=order)

            # Act & Assert
            with pytest.raises(HTTPException) as exc:
                await OrderService.get_order_by_id("order_1", "user_1")

            assert exc.value.status_code == 403

    @pytest.mark.asyncio
    async def test_get_all_orders(self, mock_order_factory):
        """Should return all orders (admin function)"""
        # Arrange
        orders = [
            mock_order_factory(user_id="user1"),
            mock_order_factory(user_id="user2"),
        ]

        with patch("app.services.order_service.Order") as MockOrder:
            MockOrder.find = MagicMock(return_value=QueryChain(orders))

            # Act
            result = await OrderService.get_all_orders()

            # Assert
            assert len(result) == 2

