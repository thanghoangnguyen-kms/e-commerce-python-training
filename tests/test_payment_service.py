"""
Unit tests for PaymentService (MockPaymentService).

- Success payment with inventory decrement
- Failure scenarios (insufficient inventory, missing product)
- Different payment outcomes
- Order not found error
- Idempotency
"""
import pytest
from unittest.mock import AsyncMock, patch

from app.services.payment_service import MockPaymentService


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

        with patch("app.services.payment_service.Order") as MockOrder, \
             patch("app.services.payment_service.Product") as MockProduct:

            MockOrder.get = AsyncMock(return_value=order)
            MockProduct.get = AsyncMock(return_value=product)

            # Act
            result = await MockPaymentService.confirm(order_id)

            # Assert
            assert result.status == "paid"
            assert product.inventory == 7  # 10 - 3
            product.save.assert_awaited_once()
            order.save.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_confirm_payment_fails_when_insufficient_inventory(
        self, mock_order_factory, mock_product_factory, mock_order_item_factory
    ):
        """Should set status to 'failed' when inventory is insufficient"""
        # Arrange
        order_item = mock_order_item_factory(product_id="prod_id", qty=10)
        order = mock_order_factory(status="pending", items=[order_item])
        product = mock_product_factory(inventory=5)

        with patch("app.services.payment_service.Order") as MockOrder, \
             patch("app.services.payment_service.Product") as MockProduct:

            MockOrder.get = AsyncMock(return_value=order)
            MockProduct.get = AsyncMock(return_value=product)

            # Act
            result = await MockPaymentService.confirm("order_id")

            # Assert
            assert result.status == "failed"

    @pytest.mark.asyncio
    async def test_confirm_payment_fails_when_product_not_found(
        self, mock_order_factory, mock_order_item_factory
    ):
        """Should set status to 'failed' when product doesn't exist"""
        # Arrange
        order_item = mock_order_item_factory(product_id="nonexistent", qty=1)
        order = mock_order_factory(status="pending", items=[order_item])

        with patch("app.services.payment_service.Order") as MockOrder, \
             patch("app.services.payment_service.Product") as MockProduct:

            MockOrder.get = AsyncMock(return_value=order)
            MockProduct.get = AsyncMock(return_value=None)

            # Act
            result = await MockPaymentService.confirm("order_id")

            # Assert
            assert result.status == "failed"

    @pytest.mark.asyncio
    async def test_confirm_payment_with_canceled_outcome(self, mock_order_factory):
        """Should set status to 'canceled' when outcome is canceled"""
        # Arrange
        order = mock_order_factory(status="pending", items=[])

        with patch("app.services.payment_service.Order") as MockOrder:
            MockOrder.get = AsyncMock(return_value=order)

            # Act
            result = await MockPaymentService.confirm("order_id", outcome="canceled")

            # Assert
            assert result.status == "canceled"

    @pytest.mark.asyncio
    async def test_confirm_payment_raises_error_when_order_not_found(self):
        """Should raise ValueError when order doesn't exist"""
        # Arrange
        with patch("app.services.payment_service.Order") as MockOrder:
            MockOrder.get = AsyncMock(return_value=None)

            # Act & Assert
            with pytest.raises(ValueError, match="Order not found"):
                await MockPaymentService.confirm("nonexistent_id")

    @pytest.mark.asyncio
    async def test_confirm_payment_is_idempotent(self, mock_order_factory):
        """Should do nothing if order already finalized (not pending)"""
        # Arrange
        order = mock_order_factory(status="paid", items=[])

        with patch("app.services.payment_service.Order") as MockOrder:
            MockOrder.get = AsyncMock(return_value=order)

            # Act
            result = await MockPaymentService.confirm("order_id")

            # Assert
            assert result.status == "paid"
            order.save.assert_not_awaited()

