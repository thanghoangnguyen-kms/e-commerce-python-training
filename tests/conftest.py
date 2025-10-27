"""Pytest configuration and fixtures for unit tests."""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from bson import ObjectId


@pytest.fixture
def mock_product():
    """Mock product data for testing."""
    return MagicMock(
        id=ObjectId("507f1f77bcf86cd799439011"),
        product_id=1,
        name="Test Product",
        slug="test-product",
        description="A test product",
        price=99.99,
        image="http://example.com/image.jpg",
        inventory=10,
        category="Electronics",
        is_active=True
    )


@pytest.fixture
def mock_user():
    """Mock user data for testing."""
    return MagicMock(
        id=ObjectId("507f1f77bcf86cd799439012"),
        email="test@example.com",
        hashed_password="$2b$12$hash",
        role="user",
        created_at=datetime.now()
    )


@pytest.fixture
def mock_admin():
    """Mock admin user data for testing."""
    return MagicMock(
        id=ObjectId("507f1f77bcf86cd799439013"),
        email="admin@example.com",
        hashed_password="$2b$12$hash",
        role="admin",
        created_at=datetime.now()
    )


@pytest.fixture
def mock_cart():
    """Mock cart data for testing."""
    from app.db.models.cart import CartItem

    return MagicMock(
        id=ObjectId("507f1f77bcf86cd799439014"),
        user_id="507f1f77bcf86cd799439012",
        items=[
            CartItem(product_id="507f1f77bcf86cd799439011", qty=2)
        ],
        save=AsyncMock()
    )


@pytest.fixture
def mock_empty_cart():
    """Mock empty cart data for testing."""
    return MagicMock(
        id=ObjectId("507f1f77bcf86cd799439015"),
        user_id="507f1f77bcf86cd799439012",
        items=[],
        save=AsyncMock()
    )


@pytest.fixture
def mock_order():
    """Mock order data for testing."""
    from app.db.models.order import OrderItem

    return MagicMock(
        id=ObjectId("507f1f77bcf86cd799439016"),
        user_id="507f1f77bcf86cd799439012",
        items=[
            OrderItem(
                product_id="507f1f77bcf86cd799439011",
                name="Test Product",
                unit_price=99.99,
                qty=2,
                line_total=199.98
            )
        ],
        total=199.98,
        status="pending",
        payment_status="pending",
        created_at=datetime.now()
    )

