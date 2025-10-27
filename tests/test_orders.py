"""Unit tests for OrderService business logic."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import HTTPException

from app.services.order_service import OrderService


class TestOrderService:
    """Test suite for OrderService."""

    @pytest.mark.asyncio
    @patch('app.services.order_service.Order')
    async def test_get_user_orders_success(self, mock_order_model, mock_order):
        """Test successfully retrieving user orders."""
        # Setup
        mock_find = MagicMock()
        mock_find.skip.return_value.limit.return_value.to_list = AsyncMock(
            return_value=[mock_order]
        )
        mock_order_model.find.return_value = mock_find

        # Execute
        result = await OrderService.get_user_orders("507f1f77bcf86cd799439012", 0, 20)

        # Assert
        assert len(result) == 1
        assert result[0] == mock_order
        mock_find.skip.assert_called_once_with(0)
        mock_find.skip.return_value.limit.assert_called_once_with(20)

    @pytest.mark.asyncio
    @patch('app.services.order_service.Order')
    async def test_get_user_orders_with_pagination(self, mock_order_model):
        """Test retrieving user orders with pagination."""
        # Setup
        mock_skip = MagicMock()
        mock_limit = MagicMock()
        mock_skip.limit.return_value = mock_limit
        mock_limit.to_list = AsyncMock(return_value=[])

        mock_find = MagicMock()
        mock_find.skip.return_value = mock_skip
        mock_order_model.find.return_value = mock_find

        # Execute
        await OrderService.get_user_orders("507f1f77bcf86cd799439012", 10, 5)

        # Assert
        mock_find.skip.assert_called_once_with(10)
        mock_skip.limit.assert_called_once_with(5)

    @pytest.mark.asyncio
    @patch('app.services.order_service.Order')
    async def test_get_user_orders_empty(self, mock_order_model):
        """Test retrieving user orders when user has no orders."""
        # Setup
        mock_find = MagicMock()
        mock_find.skip.return_value.limit.return_value.to_list = AsyncMock(return_value=[])
        mock_order_model.find.return_value = mock_find

        # Execute
        result = await OrderService.get_user_orders("507f1f77bcf86cd799439012")

        # Assert
        assert len(result) == 0

    @pytest.mark.asyncio
    @patch('app.services.order_service.Order')
    async def test_get_order_by_id_success(self, mock_order_model, mock_order):
        """Test successfully retrieving order by ID."""
        # Setup
        mock_order.user_id = "507f1f77bcf86cd799439012"
        mock_order_model.get = AsyncMock(return_value=mock_order)

        # Execute
        result = await OrderService.get_order_by_id("507f1f77bcf86cd799439016", "507f1f77bcf86cd799439012")

        # Assert
        assert result == mock_order
        mock_order_model.get.assert_called_once_with("507f1f77bcf86cd799439016")

    @pytest.mark.asyncio
    @patch('app.services.order_service.Order')
    async def test_get_order_by_id_not_found(self, mock_order_model):
        """Test retrieving non-existent order."""
        # Setup
        mock_order_model.get = AsyncMock(return_value=None)

        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            await OrderService.get_order_by_id("507f1f77bcf86cd799439016", "507f1f77bcf86cd799439012")

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Order not found"

    @pytest.mark.asyncio
    @patch('app.services.order_service.Order')
    async def test_get_order_by_id_wrong_user(self, mock_order_model, mock_order):
        """Test retrieving order that belongs to different user."""
        # Setup
        mock_order.user_id = "507f1f77bcf86cd799439099"  # Different user
        mock_order_model.get = AsyncMock(return_value=mock_order)

        # Execute & Assert
        with pytest.raises(HTTPException) as exc_info:
            await OrderService.get_order_by_id("507f1f77bcf86cd799439016", "507f1f77bcf86cd799439012")

        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "Not your order"

    @pytest.mark.asyncio
    @patch('app.services.order_service.Order')
    async def test_get_all_orders_success(self, mock_order_model, mock_order):
        """Test admin retrieving all orders."""
        # Setup
        mock_find = MagicMock()
        mock_find.skip.return_value.limit.return_value.to_list = AsyncMock(
            return_value=[mock_order, mock_order]
        )
        mock_order_model.find.return_value = mock_find

        # Execute
        result = await OrderService.get_all_orders(0, 50)

        # Assert
        assert len(result) == 2
        mock_order_model.find.assert_called_once()
        mock_find.skip.assert_called_once_with(0)
        mock_find.skip.return_value.limit.assert_called_once_with(50)

    @pytest.mark.asyncio
    @patch('app.services.order_service.Order')
    async def test_get_all_orders_with_pagination(self, mock_order_model):
        """Test admin retrieving all orders with pagination."""
        # Setup
        mock_skip = MagicMock()
        mock_limit = MagicMock()
        mock_skip.limit.return_value = mock_limit
        mock_limit.to_list = AsyncMock(return_value=[])

        mock_find = MagicMock()
        mock_find.skip.return_value = mock_skip
        mock_order_model.find.return_value = mock_find

        # Execute
        await OrderService.get_all_orders(20, 10)

        # Assert
        mock_find.skip.assert_called_once_with(20)
        mock_skip.limit.assert_called_once_with(10)

