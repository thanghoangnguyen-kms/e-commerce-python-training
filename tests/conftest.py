"""
Shared fixtures for unit tests.

Following best practices:
- Isolated fixtures using mocks
- Reusable factory fixtures
- Proper mock setup for async operations
- Clear separation of concerns
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from types import SimpleNamespace
from datetime import datetime


class QueryChain:
    """
    Mock helper for Beanie query chains.
    Simulates: Model.find().skip().limit().to_list()
    """
    def __init__(self, result):
        self._result = result

    def skip(self, *args, **kwargs):
        """Return self for method chaining"""
        return self

    def limit(self, *args, **kwargs):
        """Return self for method chaining"""
        return self

    async def to_list(self):
        """Return the mocked result"""
        return self._result


@pytest.fixture(autouse=True, scope="session")
def setup_beanie_field_mocks():
    """
    Setup Beanie field sentinels for query operations.
    This allows `Model.field == value` to work in isolated unit tests.
    """
    from app.db.models.user import User
    from app.db.models.cart import Cart
    from app.db.models.product import Product
    from app.db.models.order import Order

    models_and_fields = [
        (User, ["email", "role"]),
        (Cart, ["user_id"]),
        (Product, ["slug", "product_id", "is_active"]),
        (Order, ["user_id"]),
    ]

    for model_cls, fields in models_and_fields:
        for field_name in fields:
            if not hasattr(model_cls, field_name):
                setattr(model_cls, field_name, MagicMock(name=f"{model_cls.__name__}.{field_name}"))


# ==================== Factory Fixtures ====================

@pytest.fixture
def mock_user_factory():
    """
    Factory fixture for creating mock User objects.
    Usage: user = mock_user_factory(email="test@example.com")
    """
    def _create(**overrides):
        defaults = {
            "id": "507f1f77bcf86cd799439011",
            "email": "test@example.com",
            "hashed_password": "$2b$12$hashedpassword",
            "role": "user",
            "created_at": datetime.utcnow(),
        }
        defaults.update(overrides)

        user = SimpleNamespace(**defaults)
        user.insert = AsyncMock(return_value=user)
        user.save = AsyncMock(return_value=user)
        return user
    return _create


@pytest.fixture
def mock_product_factory():
    """
    Factory fixture for creating mock Product objects.
    Usage: product = mock_product_factory(name="Widget")
    """
    def _create(**overrides):
        defaults = {
            "id": "507f1f77bcf86cd799439012",
            "product_id": 1,
            "name": "Test Product",
            "slug": "test-product",
            "description": "A test product description",
            "price": 99.99,
            "image": "http://example.com/product.jpg",
            "inventory": 10,
            "category": "Electronics",
            "is_active": True,
            "created_at": datetime.utcnow(),
        }
        defaults.update(overrides)

        product = SimpleNamespace(**defaults)
        product.insert = AsyncMock(return_value=product)
        product.save = AsyncMock(return_value=product)
        
        # Add model_dump() method to support serialization with mode and exclude parameters
        def model_dump(mode=None, exclude=None):
            result = {k: v for k, v in defaults.items()}
            # Handle exclude parameter to filter out specified fields
            if exclude:
                result = {k: v for k, v in result.items() if k not in exclude}
            return result
        product.model_dump = model_dump
        
        return product
    return _create


@pytest.fixture
def mock_cart_factory():
    """
    Factory fixture for creating mock Cart objects.
    Usage: cart = mock_cart_factory(items=[...])
    """
    def _create(items=None, **overrides):
        from app.db.models.cart import CartItem

        if items is None:
            items = []

        defaults = {
            "id": "507f1f77bcf86cd799439013",
            "user_id": "507f1f77bcf86cd799439011",
            "items": items,
        }
        defaults.update(overrides)

        cart = SimpleNamespace(**defaults)
        cart.insert = AsyncMock(return_value=cart)
        cart.save = AsyncMock(return_value=cart)
        return cart
    return _create


@pytest.fixture
def mock_order_factory():
    """
    Factory fixture for creating mock Order objects.
    Usage: order = mock_order_factory(total=100.0)
    """
    def _create(items=None, **overrides):
        if items is None:
            items = []

        defaults = {
            "id": "507f1f77bcf86cd799439014",
            "user_id": "507f1f77bcf86cd799439011",
            "items": items,
            "total": 0.0,
            "status": "pending",
            "created_at": datetime.utcnow(),
        }
        defaults.update(overrides)

        order = SimpleNamespace(**defaults)
        order.insert = AsyncMock(return_value=order)
        order.save = AsyncMock(return_value=order)
        
        # Add model_dump() method to support serialization with mode and exclude parameters
        def model_dump(mode=None, exclude=None):
            result = {k: v for k, v in defaults.items()}
            # Handle exclude parameter to filter out specified fields
            if exclude:
                result = {k: v for k, v in result.items() if k not in exclude}
            return result
        order.model_dump = model_dump
        
        return order
    return _create


@pytest.fixture
def mock_cart_item_factory():
    """
    Factory fixture for creating CartItem objects.
    Usage: item = mock_cart_item_factory(product_id="123", qty=2)
    """
    def _create(**overrides):
        from app.db.models.cart import CartItem

        defaults = {
            "product_id": 1,  # Changed from string to integer
            "qty": 1,
        }
        defaults.update(overrides)
        return CartItem(**defaults)
    return _create


@pytest.fixture
def mock_order_item_factory():
    """
    Factory fixture for creating OrderItem objects.
    Usage: item = mock_order_item_factory(name="Widget", qty=2)
    """
    def _create(**overrides):
        from app.db.models.order import OrderItem

        defaults = {
            "product_id": "507f1f77bcf86cd799439012",
            "name": "Test Product",
            "unit_price": 99.99,
            "qty": 1,
            "line_total": 99.99,
        }
        defaults.update(overrides)
        return OrderItem(**defaults)
    return _create
