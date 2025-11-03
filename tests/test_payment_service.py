"""
Unit tests for PaymentService (MockPaymentService).

- Success payment with inventory decrement
- Failure scenarios (insufficient inventory, missing product)
- Different payment outcomes
- Order not found error
- Idempotency
"""
import pytest
from unittest.mock import Mock, AsyncMock
from fastapi import HTTPException

from app.services.payment_service import MockPaymentService
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository


class TestPaymentServiceConfirm:
    """Test cases for payment confirmation"""

    @pytest.mark.asyncio
    async def test_confirm_payment_success(
        self, mock_order_factory, mock_product_factory, mock_order_item_factory
    ):
        """Should update status to 'paid' and decrement inventory on success"""
        # Arrange
        order_id = "test_order_id"
        product_id = "test_product_id"
        initial_inventory = 10
        order_qty = 3

        order_item = mock_order_item_factory(product_id=product_id, qty=order_qty)
        order = mock_order_factory(id=order_id, status="pending", items=[order_item])
        product = mock_product_factory(id=product_id, inventory=initial_inventory)
        
        mock_order_repo = Mock(spec=OrderRepository)
        mock_order_repo.get_by_id = AsyncMock(return_value=order)
        mock_order_repo.update = AsyncMock(return_value=order)
        
        mock_product_repo = Mock(spec=ProductRepository)
        mock_product_repo.get_by_id = AsyncMock(return_value=product)
        mock_product_repo.decrement_inventory = AsyncMock()
        
        service = MockPaymentService(
            order_repository=mock_order_repo,
            product_repository=mock_product_repo
        )

        # Act
        result = await service.confirm(order_id)

        # Assert
        assert result.status == "paid"
        mock_product_repo.decrement_inventory.assert_called_once_with(product_id, order_qty)
        mock_order_repo.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_confirm_payment_fails_when_insufficient_inventory(
        self, mock_order_factory, mock_product_factory, mock_order_item_factory
    ):
        """Should raise HTTPException when inventory is insufficient"""
        # Arrange
        order_item = mock_order_item_factory(product_id="prod_id", qty=10)
        order = mock_order_factory(status="pending", items=[order_item])
        product = mock_product_factory(inventory=5)
        
        mock_order_repo = Mock(spec=OrderRepository)
        mock_order_repo.get_by_id = AsyncMock(return_value=order)
        mock_order_repo.update = AsyncMock(return_value=order)
        
        mock_product_repo = Mock(spec=ProductRepository)
        mock_product_repo.get_by_id = AsyncMock(return_value=product)
        
        service = MockPaymentService(
            order_repository=mock_order_repo,
            product_repository=mock_product_repo
        )

        # Act & Assert
        with pytest.raises(HTTPException) as exc:
            await service.confirm("order_id")
        
        assert exc.value.status_code == 400
        assert "Insufficient inventory" in str(exc.value.detail)
        mock_order_repo.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_confirm_payment_fails_when_product_not_found(
        self, mock_order_factory, mock_order_item_factory
    ):
        """Should raise HTTPException when product doesn't exist"""
        # Arrange
        order_item = mock_order_item_factory(product_id="nonexistent", qty=1)
        order = mock_order_factory(status="pending", items=[order_item])
        
        mock_order_repo = Mock(spec=OrderRepository)
        mock_order_repo.get_by_id = AsyncMock(return_value=order)
        mock_order_repo.update = AsyncMock(return_value=order)
        
        mock_product_repo = Mock(spec=ProductRepository)
        mock_product_repo.get_by_id = AsyncMock(return_value=None)
        
        service = MockPaymentService(
            order_repository=mock_order_repo,
            product_repository=mock_product_repo
        )

        # Act & Assert
        with pytest.raises(HTTPException) as exc:
            await service.confirm("order_id")
        
        assert exc.value.status_code == 400
        assert "Insufficient inventory" in str(exc.value.detail)
        mock_order_repo.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_confirm_payment_with_canceled_outcome(self, mock_order_factory):
        """Should set status to 'canceled' when outcome is canceled"""
        # Arrange
        order = mock_order_factory(status="pending", items=[])
        
        mock_order_repo = Mock(spec=OrderRepository)
        mock_order_repo.get_by_id = AsyncMock(return_value=order)
        mock_order_repo.update = AsyncMock(return_value=order)
        
        service = MockPaymentService(order_repository=mock_order_repo)

        # Act
        result = await service.confirm("order_id", outcome="canceled")

        # Assert
        assert result.status == "canceled"
        mock_order_repo.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_confirm_payment_raises_error_when_order_not_found(self):
        """Should raise HTTPException when order doesn't exist"""
        # Arrange
        mock_order_repo = Mock(spec=OrderRepository)
        mock_order_repo.get_by_id = AsyncMock(return_value=None)
        
        service = MockPaymentService(order_repository=mock_order_repo)

        # Act & Assert
        with pytest.raises(HTTPException) as exc:
            await service.confirm("nonexistent_id")
        
        assert exc.value.status_code == 404
        assert "Order not found" in str(exc.value.detail)

    @pytest.mark.asyncio
    async def test_confirm_payment_is_idempotent(self, mock_order_factory):
        """Should do nothing if order already finalized (not pending)"""
        # Arrange
        order = mock_order_factory(status="paid", items=[])
        
        mock_order_repo = Mock(spec=OrderRepository)
        mock_order_repo.get_by_id = AsyncMock(return_value=order)
        
        service = MockPaymentService(order_repository=mock_order_repo)

        # Act
        result = await service.confirm("order_id")

        # Assert
        assert result.status == "paid"
        mock_order_repo.update.assert_not_called()
