"""
Service dependency providers for FastAPI dependency injection.
Creates service instances with their required repositories.
"""
from app.services.auth_service import AuthService
from app.services.product_service import ProductService
from app.services.cart_service import CartService
from app.services.order_service import OrderService
from app.services.checkout_service import CheckoutService
from app.services.payment_service import MockPaymentService


def get_auth_service() -> AuthService:
    """Provide AuthService instance."""
    return AuthService()


def get_product_service() -> ProductService:
    """Provide ProductService instance."""
    return ProductService()


def get_cart_service() -> CartService:
    """Provide CartService instance."""
    return CartService()


def get_order_service() -> OrderService:
    """Provide OrderService instance."""
    return OrderService()


def get_checkout_service() -> CheckoutService:
    """Provide CheckoutService instance."""
    return CheckoutService()


def get_payment_service() -> MockPaymentService:
    """Provide MockPaymentService instance."""
    return MockPaymentService()

