from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from contextlib import asynccontextmanager
import logging
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.cache import cache_manager
from app.db.init import db_manager
from app.api.routers.auth_router import router as auth_router
from app.api.routers.product_router import router as product_router
from app.api.routers.cart_router import router as cart_router
from app.api.routers.checkout_router import router as checkout_router
from app.api.routers.admin_router import router as admin_router
from app.api.routers.payment_router import router as payment_router
from app.api.routers.order_router import router as order_router
from app.api.middleware import LoggingMiddleware
from app.api.rate_limit import limiter, rate_limit_exceeded_handler

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifespan: startup and shutdown events.
    """
    # Startup
    logger.info("Starting up E-Commerce API...")
    try:
        await cache_manager.initialize()
        await db_manager.initialize(settings.mongodb_uri)
        logger.info("Application startup complete")
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise
    
    yield
    
    # Shutdown
    await cache_manager.close()
    logger.info("Shutting down E-Commerce API...")
    await db_manager.close()
    logger.info("Application shutdown complete")


app = FastAPI(
    lifespan=lifespan,
    title="E-Commerce API",
    description="""
## E-Commerce Platform API

A comprehensive REST API for managing an e-commerce platform with user authentication, 
product management, shopping cart, and order processing.

### Features:
* **Authentication**: JWT-based user authentication with role-based access control
* **Product Management**: Browse and search products, admin product CRUD operations
* **Shopping Cart**: Add/remove items, manage cart
* **Checkout & Orders**: Create orders from cart items
* **Payment Processing**: Mock payment confirmation (ready for real gateway integration)
* **Rate Limiting**: Protection against abuse with per-endpoint rate limits

### Authentication:
1. First, use `/auth/signup` or `/auth/login` to get your access token
2. Click the **Authorize 🔓** button at the top right
3. Enter your token in the format: `Bearer <your_access_token>` or just paste the token directly
4. Click **Authorize** - now all protected endpoints will use this token automatically!

**Note:** You only need to authorize once, and it will apply to all requests in this session.
    """,
    version="1.0.0",
    contact={
        "name": "E-Commerce API Support",
        "email": "support@example.com",
    },
    swagger_ui_parameters={
        "defaultModelsExpandDepth": 1,
        "docExpansion": "none",
        "persistAuthorization": True,
    }
)

# Add rate limiter state to app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# Custom OpenAPI schema to add security definitions
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Add security scheme for Bearer token
    openapi_schema["components"]["securitySchemes"] = {
        "Bearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter your JWT token from login/signup"
        }
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods.split(",") if settings.cors_allow_methods != "*" else ["*"],
    allow_headers=settings.cors_allow_headers.split(",") if settings.cors_allow_headers != "*" else ["*"],
)

# Add logging middleware
app.add_middleware(LoggingMiddleware)

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(product_router, prefix="/products", tags=["products"])
app.include_router(cart_router, prefix="/cart", tags=["cart"])
app.include_router(checkout_router, prefix="/checkout", tags=["checkout"])
app.include_router(admin_router, prefix="/admin", tags=["admin"])
app.include_router(order_router, prefix="/orders", tags=["orders"])
app.include_router(payment_router, prefix="/payments", tags=["payments"])
