# E-Commerce Python Training - Complete Project Context

**Last Updated:** 2025-11-04  
**Project Version:** 1.0.0  
**Tech Stack:** FastAPI, MongoDB, Redis, Beanie ODM, JWT

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture & Design Patterns](#architecture--design-patterns)
3. [Tech Stack & Dependencies](#tech-stack--dependencies)
4. [Project Structure](#project-structure)
5. [Core Components](#core-components)
6. [Database Models](#database-models)
7. [Repository Layer](#repository-layer)
8. [Service Layer](#service-layer)
9. [API Layer](#api-layer)
10. [Authentication & Security](#authentication--security)
11. [Caching Strategy](#caching-strategy)
12. [Configuration & Environment](#configuration--environment)
13. [Testing Strategy](#testing-strategy)
14. [Deployment & Docker](#deployment--docker)

---

## 📖 Project Overview

A production-ready REST API for e-commerce applications featuring:

- **Authentication:** JWT-based with 15-minute token expiration
- **User Roles:** Regular users and admins with role-based access control
- **Product Management:** CRUD operations with search and filtering
- **Shopping Cart:** Add/remove items, quantity management
- **Order Processing:** Cart-to-order conversion with payment simulation
- **Caching:** Redis-based caching with automatic invalidation
- **Rate Limiting:** IP-based rate limiting (5 req/min for product endpoints)
- **Database:** MongoDB with Beanie ODM for async operations

### Key Features

- ✅ Clean architecture with layered design (API → Service → Repository → Database)
- ✅ Dependency injection pattern for testability
- ✅ Redis caching with performance monitoring
- ✅ Comprehensive logging and middleware
- ✅ Docker containerization
- ✅ Automatic database seeding (admin user + 20 sample products)
- ✅ CORS configuration for frontend integration
- ✅ Interactive API documentation (Swagger UI)

---

## 🏗️ Architecture & Design Patterns

### Layered Architecture

```
┌─────────────────────────────────────────┐
│         API Layer (Routers)             │  ← FastAPI routes, request validation
├─────────────────────────────────────────┤
│      Service Layer (Business Logic)     │  ← Core business rules, orchestration
├─────────────────────────────────────────┤
│    Repository Layer (Data Access)       │  ← Database queries, CRUD operations
├─────────────────────────────────────────┤
│      Database Layer (Models)            │  ← Beanie ODM models, MongoDB
└─────────────────────────────────────────┘
```

### Design Patterns Used

1. **Repository Pattern**: Abstracts data access logic
2. **Service Pattern**: Encapsulates business logic
3. **Dependency Injection**: Services and repositories injected via FastAPI
4. **Singleton Pattern**: Database manager, cache manager
5. **Decorator Pattern**: `@cached`, `@service_method` decorators
6. **Factory Pattern**: Test fixtures for mock object creation

---

## 🔧 Tech Stack & Dependencies

### Core Dependencies (pyproject.toml)

```toml
[project]
name = "ecommerce-api"
version = "0.1.0"
requires-python = ">=3.11"
dependencies = [
  "fastapi>=0.115.0",           # Web framework
  "uvicorn[standard]>=0.30.0",  # ASGI server
  "beanie>=1.26.0",             # MongoDB ODM
  "pydantic[email]>=2.5.0",     # Data validation
  "python-dotenv>=1.0.1",       # Environment variables
  "motor>=3.5.0",               # Async MongoDB driver
  "bcrypt>=4.1.2",              # Password hashing
  "pyjwt>=2.9.0",               # JWT tokens
  "httpx>=0.27.0",              # HTTP client
  "slowapi>=0.1.9",             # Rate limiting
  "redis>=5.0.0"                # Caching
]
```

### Infrastructure

- **Database:** MongoDB 6.0+ (NoSQL document database)
- **Cache:** Redis 7.0+ (In-memory data store)
- **Container:** Docker + Docker Compose
- **Package Manager:** uv (fast Python package installer)

---

## 📁 Project Structure

```
e-commerce-python-training/
├── app/
│   ├── __init__.py
│   ├── main.py                      # FastAPI application entry point
│   │
│   ├── api/                         # API Layer
│   │   ├── deps.py                  # Auth dependencies (get_current_user, admin_required)
│   │   ├── middleware.py            # Logging middleware
│   │   ├── rate_limit.py            # Rate limiting configuration
│   │   ├── service_deps.py          # Service injection providers
│   │   └── routers/                 # API endpoints
│   │       ├── auth_router.py       # /auth/* - signup, login, me
│   │       ├── product_router.py    # /products/* - list, get by slug
│   │       ├── cart_router.py       # /cart/* - get, add, remove
│   │       ├── checkout_router.py   # /checkout/* - create order
│   │       ├── order_router.py      # /orders/* - list, get details
│   │       ├── payment_router.py    # /payments/* - confirm payment
│   │       └── admin_router.py      # /admin/* - product CRUD
│   │
│   ├── core/                        # Core Functionality
│   │   ├── config.py                # Environment configuration (Settings)
│   │   ├── security.py              # Password hashing (bcrypt)
│   │   ├── jwt.py                   # JWT token creation/validation
│   │   ├── cache.py                 # Redis cache manager (CacheManager)
│   │   ├── cache_decorator.py       # @cached decorator with performance logging
│   │   └── service_decorator.py     # @service_method decorator
│   │
│   ├── db/                          # Database Layer
│   │   ├── init.py                  # Database initialization (DatabaseManager)
│   │   ├── seed.py                  # Database seeding (admin + 20 products)
│   │   └── models/                  # Beanie ODM models
│   │       ├── user.py              # User model (email, hashed_password, role)
│   │       ├── product.py           # Product model (product_id, name, slug, etc.)
│   │       ├── cart.py              # Cart model (user_id, items[])
│   │       └── order.py             # Order model (user_id, items[], total, status)
│   │
│   ├── repositories/                # Repository Layer (Data Access)
│   │   ├── base_repository.py       # Generic CRUD operations
│   │   ├── user_repository.py       # User-specific queries
│   │   ├── product_repository.py    # Product search, inventory management
│   │   ├── cart_repository.py       # Cart operations
│   │   └── order_repository.py      # Order queries
│   │
│   ├── services/                    # Service Layer (Business Logic)
│   │   ├── auth_service.py          # User registration, login, promotion
│   │   ├── product_service.py       # Product listing, search, CRUD (with caching)
│   │   ├── cart_service.py          # Cart management
│   │   ├── checkout_service.py      # Order creation from cart
│   │   ├── order_service.py         # Order retrieval
│   │   └── payment_service.py       # Mock payment processing
│   │
│   ├── schemas/                     # Pydantic Schemas (Request/Response)
│   │   ├── auth.py                  # SignupRequest, LoginRequest, TokenResponse
│   │   ├── product.py               # ProductCreateRequest, ProductUpdateRequest
│   │   ├── cart.py                  # CartItemRequest, CartRemoveRequest
│   │   ├── order.py                 # OrderCreateResponse
│   │   └── payment.py               # PaymentConfirmResponse
│   │
│   └── scripts/                     # Utility Scripts
│       └── create_admin.py          # Manual admin user creation
│
├── tests/                           # Test Suite
│   ├── conftest.py                  # Shared test fixtures
│   ├── test_auth_service.py         # Auth service tests
│   ├── test_product_service.py      # Product service tests
│   ├── test_cart_service.py         # Cart service tests
│   ├── test_checkout_service.py     # Checkout service tests
│   ├── test_order_service.py        # Order service tests
│   └── test_payment_service.py      # Payment service tests
│
├── docker-compose.yml               # Multi-container orchestration
├── Dockerfile                       # API container definition
├── pyproject.toml                   # Project dependencies
├── pytest.ini                       # Pytest configuration
├── README.md                        # Project documentation
└── .env                             # Environment variables (not in git)
```

---

## 🔑 Core Components

### 1. Main Application (app/main.py)

**Purpose:** FastAPI application entry point with lifespan management

**Key Features:**
- Lifespan context manager for startup/shutdown
- Database initialization on startup
- Redis cache initialization
- CORS middleware configuration
- Logging middleware
- Rate limiting setup
- Router inclusion
- Custom OpenAPI schema with Bearer auth

**Startup Sequence:**
```python
1. Initialize Redis connection → cache_manager.initialize()
2. Initialize MongoDB → db_manager.initialize(settings.mongodb_uri)
3. Seed database → create admin user + 20 sample products
4. Start accepting requests
```

**Shutdown Sequence:**
```python
1. Close Redis connection → cache_manager.close()
2. Close MongoDB connection → db_manager.close()
```

---

### 2. Configuration (app/core/config.py)

**Purpose:** Centralized configuration using environment variables

**Settings Class:**
```python
class Settings(BaseModel):
    # Database
    mongodb_uri: str = "mongodb://localhost:27017/ecommerce"
    
    # JWT
    jwt_secret: str = "change_me"  # ⚠️ MUST change in production
    jwt_alg: str = "HS256"
    access_exp_min: int = 15  # Token expires in 15 minutes
    
    # Redis Cache
    redis_url: str = "redis://localhost:6379"
    redis_enabled: bool = True
    cache_ttl_seconds: int = 300  # 5 minutes default
    
    # Admin User (Auto-created on startup)
    create_default_admin: bool = True
    default_admin_email: str = "admin@example.com"
    default_admin_password: str = "admin123"  # ⚠️ Change in production
    
    # CORS
    cors_origins: str = "http://localhost:3000,..."  # Frontend URLs
    cors_allow_credentials: bool = True
    cors_allow_methods: str = "*"
    cors_allow_headers: str = "*"
```

**Environment Variables:**
- All settings can be overridden via `.env` file
- Example: `MONGODB_URI=mongodb://mongo:27017/ecommerce`

---

### 3. Security (app/core/security.py & jwt.py)

#### Password Hashing (security.py)
```python
def hash_password(pw: str) -> str:
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()

def verify_password(pw: str, hashed: str) -> bool:
    return bcrypt.checkpw(pw.encode(), hashed.encode())
```

#### JWT Tokens (jwt.py)
```python
def create_token(sub: str, role: str, minutes: int):
    payload = {
        "sub": user_id,      # MongoDB ObjectId string
        "role": role,        # "user" or "admin"
        "iat": now,          # Issued at
        "exp": now + minutes*60  # Expires in 15 minutes
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")

def decode_token(token: str):
    return jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
```

**Token Structure:**
```json
{
  "sub": "507f1f77bcf86cd799439011",  // User ID
  "role": "user",                      // Role
  "iat": 1729536191,                   // Issued at
  "exp": 1729537091                    // Expires at (15 min later)
}
```

---

### 4. Cache Manager (app/core/cache.py)

**Purpose:** Redis-based caching with automatic serialization

**Key Features:**
- Singleton pattern for connection reuse
- Automatic JSON serialization/deserialization
- Beanie Document serialization support
- TTL (Time To Live) management
- Pattern-based invalidation
- Graceful degradation if Redis unavailable

**Main Methods:**
```python
class CacheManager:
    async def get(namespace, key) -> Any | None
    async def set(namespace, key, value, ttl=None) -> bool
    async def delete(namespace, key) -> bool
    async def delete_pattern(namespace, pattern) -> int
    async def clear_namespace(namespace) -> int
```

**Cache Key Format:**
```
ecommerce:{namespace}:{key}

Examples:
- ecommerce:products:list:q=all:skip=0:limit=20
- ecommerce:products:slug:gaming-laptop-pro
- ecommerce:users:email:user@example.com
```

**Usage in Services:**
```python
@cached(
    namespace="products",
    key_builder=lambda self, slug: f"slug:{slug}"
)
async def get_product_by_slug(self, slug: str) -> Product:
    # This method result is automatically cached
    # Cache key: ecommerce:products:slug:gaming-laptop-pro
    pass
```

---

### 5. Cache Decorator (app/core/cache_decorator.py)

**Purpose:** Automatic caching with performance monitoring

**Features:**
- Transparent caching for async functions
- Automatic cache key building from function arguments
- Performance logging (cache hit/miss, execution time)
- Configurable TTL per decorator

**Example Usage:**
```python
@cached(
    namespace="products",
    key_builder=lambda self, q=None, skip=0, limit=20: 
        f"list:q={q or 'all'}:skip={skip}:limit={limit}",
    ttl=300,  # 5 minutes
    log_performance=True
)
async def list_products(self, q=None, skip=0, limit=20):
    # Function body executes only on cache miss
    return await Product.find(...).to_list()
```

**Performance Logs:**
```
✅ CACHE HIT [products]: Key 'list:q=all:skip=0:limit=20' retrieved in 2.34ms from Redis
❌ CACHE MISS [products]: Key 'list:q=laptop:skip=0:limit=20' not found (lookup: 1.89ms)
📊 FUNCTION EXECUTED [products]: Took 45.67ms to complete
💾 CACHED [products]: Stored result in Redis (3.21ms)
⏱️  TOTAL TIME [products]: 50.77ms (Cache check: 1.89ms + Execution: 45.67ms + Cache store: 3.21ms)
```

**Cache Invalidation:**
```python
# Invalidate specific cache entry
await invalidate_cache("products", "slug:gaming-laptop-pro")

# Invalidate pattern (all product lists)
await invalidate_cache("products", "list:*")

# Clear entire namespace
await invalidate_cache("products", "*")
```

---

## 💾 Database Models

### 1. User Model (app/db/models/user.py)

```python
class User(Document):
    email: Indexed(EmailStr, unique=True)  # Unique indexed email
    hashed_password: str                   # Bcrypt hash
    role: str = "user"                     # "user" | "admin"
    created_at: datetime = datetime.utcnow()

    class Settings:
        name = "users"  # MongoDB collection name
```

**Indexes:**
- `email` (unique): Fast user lookup by email

---

### 2. Product Model (app/db/models/product.py)

```python
class Product(Document):
    product_id: Indexed(int, unique=True)  # Business ID (1, 2, 3...)
    name: Indexed(str)                     # Indexed for search
    slug: Indexed(str, unique=True)        # URL-friendly ID
    description: str | None
    price: float                           # USD, must be > 0
    image: str | None                      # Image URL
    inventory: int = 0                     # Available quantity
    category: str | None                   # "Electronics", "Fashion", etc.
    is_active: bool = True                 # Soft delete flag
    created_at: datetime = datetime.utcnow()

    class Settings:
        name = "products"
```

**Indexes:**
- `product_id` (unique): Business identifier
- `slug` (unique): URL-friendly lookup
- `name`: Text search support

**Important:** 
- Products have TWO IDs:
  1. `id` (MongoDB ObjectId) - Database internal ID
  2. `product_id` (integer) - Business/public ID (e.g., 1, 2, 3...)
- Cart stores `product_id` (integer) for simplicity
- Orders store MongoDB `id` (string) for referential integrity

---

### 3. Cart Model (app/db/models/cart.py)

```python
class CartItem(BaseModel):
    product_id: int  # Integer product_id (not MongoDB _id)
    qty: int         # Quantity

class Cart(Document):
    user_id: Indexed(str)              # User's MongoDB ObjectId string
    items: list[CartItem] = []         # Cart items
    updated_at: datetime = datetime.utcnow()

    class Settings:
        name = "carts"
```

**Design Decision:**
- Cart stores `product_id` (integer) not MongoDB ObjectId
- Simpler for frontend/API (no need to know internal IDs)
- Lookup products by `product_id` when processing cart

---

### 4. Order Model (app/db/models/order.py)

```python
class OrderItem(BaseModel):
    product_id: str      # MongoDB ObjectId string (referential integrity)
    name: str            # Snapshot of product name
    unit_price: float    # Snapshot of price at order time
    qty: int             # Quantity ordered
    line_total: float    # unit_price * qty

class Order(Document):
    user_id: Indexed(str)              # User's MongoDB ObjectId string
    items: list[OrderItem]             # Order items (snapshots)
    total: float                       # Total order amount
    currency: str = "usd"              # Currency code
    status: str = "pending"            # "pending" | "paid" | "canceled" | "failed"
    created_at: datetime = datetime.utcnow()

    class Settings:
        name = "orders"
```

**Order Status Flow:**
```
pending → paid     (payment successful)
        → failed   (payment failed or insufficient inventory)
        → canceled (user canceled)
```

**Design Decision:**
- Order items store MongoDB ObjectId (string) for referential integrity
- Order items are snapshots (price/name at order time)
- Inventory NOT decremented until payment confirmed

---

## 🗄️ Repository Layer

### Base Repository (app/repositories/base_repository.py)

**Purpose:** Generic CRUD operations for all models

```python
class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T]):
        self.model = model

    async def get_by_id(id: str) -> T | None
    async def find_one(*args, **kwargs) -> T | None
    async def find_many(*args, skip=0, limit=100) -> list[T]
    async def find_all(skip=0, limit=100) -> list[T]
    async def create(document: T) -> T
    async def update(document: T) -> T
    async def delete(document: T) -> None
    async def count(*args, **kwargs) -> int
```

**Inheritance Example:**
```python
class ProductRepository(BaseRepository[Product]):
    def __init__(self):
        super().__init__(Product)
    
    # Add product-specific methods
    async def find_by_slug(slug: str) -> Product | None
    async def find_by_product_id(product_id: int) -> Product | None
    async def search_products(query: str, skip: int, limit: int) -> list[Product]
```

---

### Product Repository (app/repositories/product_repository.py)

**Special Methods:**
```python
async def find_by_slug(slug: str, active_only=True) -> Product | None
    # Find product by URL slug (e.g., "gaming-laptop-pro")

async def find_by_product_id(product_id: int) -> Product | None
    # Find product by business ID (e.g., 1, 2, 3...)

async def search_products(search_query=None, skip=0, limit=20) -> list[Product]
    # Search by name or category (case-insensitive regex)
    # Query: {"$or": [{"name": {"$regex": query, "$options": "i"}}, ...]}

async def decrement_inventory(product_id: str, quantity: int) -> Product | None
    # Reduce inventory after payment confirmation
    # Uses MongoDB ObjectId string
```

---

### Cart Repository (app/repositories/cart_repository.py)

**Special Methods:**
```python
async def find_by_user_id(user_id: str) -> Cart | None
    # Get user's cart

async def get_or_create_cart(user_id: str) -> Cart
    # Get existing cart or create new empty cart

async def add_item(user_id: str, product_id: int, quantity: int) -> Cart
    # Add item or increment quantity if exists
    # Uses integer product_id

async def remove_item(user_id: str, product_id: int) -> Cart | None
    # Remove item completely from cart

async def clear_cart(user_id: str) -> Cart | None
    # Remove all items (called after order creation)
```

---

### Order Repository (app/repositories/order_repository.py)

**Special Methods:**
```python
async def find_by_user_id(user_id: str, skip=0, limit=20) -> list[Order]
    # Get all orders for a user (paginated)

async def find_by_id_and_user(order_id: str, user_id: str) -> Order | None
    # Get order and verify ownership (security check)

async def update_status(order_id: str, status: str) -> Order | None
    # Update order status (pending → paid/failed/canceled)
```

---

## 🎯 Service Layer

### 1. Auth Service (app/services/auth_service.py)

**Responsibility:** User authentication and authorization

**Key Methods:**

```python
async def signup_user(email: str, password: str) -> dict:
    # 1. Check if email already exists
    # 2. Hash password with bcrypt
    # 3. Create User document
    # 4. Generate JWT token (15 min expiry)
    # Returns: {"access_token": "...", "token_type": "bearer"}

async def login_user(email: str, password: str) -> dict:
    # 1. Find user by email
    # 2. Verify password with bcrypt
    # 3. Generate JWT token (15 min expiry)
    # Raises HTTPException(401) if invalid credentials

async def get_user_by_id(user_id: str) -> User:
    # Get user by MongoDB ObjectId
    # Raises HTTPException(404) if not found

async def promote_user_to_admin(email: str) -> User:
    # 1. Find user by email
    # 2. Change role to "admin"
    # 3. Save and return updated user
    # Raises HTTPException(404) if user not found
    # Raises HTTPException(400) if already admin
```

**Security Features:**
- Password hashing with bcrypt (salt automatically generated)
- JWT tokens with 15-minute expiration
- Role-based access control

---

### 2. Product Service (app/services/product_service.py)

**Responsibility:** Product management with caching

**Key Methods:**

```python
@cached(namespace="products", key_builder=...)
async def list_products(search_query=None, skip=0, limit=20) -> list[Product]:
    # 1. Check cache first
    # 2. If cache miss, query database
    # 3. Cache results for 5 minutes (default TTL)
    # Supports search by name/category

@cached(namespace="products", key_builder=lambda self, slug: f"slug:{slug}")
async def get_product_by_slug(slug: str) -> Product:
    # 1. Check cache first
    # 2. If cache miss, query database
    # 3. Cache result
    # Raises HTTPException(404) if not found or inactive

async def create_product(...) -> Product:
    # 1. Validate slug uniqueness
    # 2. Validate product_id uniqueness
    # 3. Create product document
    # 4. Invalidate all list caches (new product added)
    # Returns: Product with MongoDB id

async def update_product(product_id: str, ...) -> Product:
    # 1. Find product by MongoDB ObjectId
    # 2. Validate new product_id if changed
    # 3. Update all fields
    # 4. Invalidate specific product cache + all list caches

async def delete_product(product_id: str) -> dict:
    # 1. Find product by MongoDB ObjectId
    # 2. Delete from database
    # 3. Invalidate specific product cache + all list caches
    # Returns: Confirmation with deleted product details
```

**Caching Strategy:**
- List results cached by query params
- Individual products cached by slug
- Cache invalidation on create/update/delete
- TTL: 5 minutes (configurable)

---

### 3. Cart Service (app/services/cart_service.py)

**Responsibility:** Shopping cart management

**Key Methods:**

```python
async def get_or_create_cart(user_id: str) -> Cart:
    # Get existing cart or create new empty cart

async def add_item_to_cart(user_id: str, product_id: int, qty: int) -> Cart:
    # 1. Validate product exists and is active (by product_id)
    # 2. Validate quantity > 0
    # 3. Add item to cart or increment quantity if exists
    # Uses integer product_id (not MongoDB ObjectId)

async def remove_item_from_cart(user_id: str, product_id: int) -> Cart:
    # 1. Validate product exists
    # 2. Remove item from cart completely (regardless of quantity)

async def clear_cart(user_id: str) -> Cart:
    # Remove all items from cart
```

**Design Notes:**
- Cart items use integer `product_id` (not MongoDB ObjectId)
- Simpler for frontend integration
- Product validation ensures only active products can be added

---

### 4. Checkout Service (app/services/checkout_service.py)

**Responsibility:** Convert cart to order

**Key Method:**

```python
async def create_order_from_cart(user_id: str) -> Order:
    # 1. Get user's cart
    # 2. Validate cart not empty
    # 3. For each cart item:
    #    - Look up product by integer product_id
    #    - Validate product active and available
    #    - Calculate line total
    #    - Create OrderItem (stores MongoDB ObjectId string)
    # 4. Calculate total
    # 5. Create Order document (status="pending")
    # 6. Clear cart
    # 7. Return order
    
    # Note: Inventory NOT decremented yet (waits for payment)
```

**Order vs Cart Item Structure:**
```python
# Cart Item (temporary)
{
    "product_id": 1,  # Integer (business ID)
    "qty": 2
}

# Order Item (permanent snapshot)
{
    "product_id": "507f1f77bcf86cd799439012",  # MongoDB ObjectId string
    "name": "Gaming Laptop Pro",               # Snapshot
    "unit_price": 1499.99,                     # Snapshot
    "qty": 2,
    "line_total": 2999.98
}
```

---

### 5. Payment Service (app/services/payment_service.py)

**Responsibility:** Payment processing (mock implementation)

**Key Method:**

```python
async def confirm(order_id: str, outcome: "success"|"failure"|"canceled") -> Order:
    # 1. Get order by MongoDB ObjectId
    # 2. Validate order status is "pending" (idempotent)
    # 3. If outcome == "success":
    #    - For each order item:
    #      - Get product by MongoDB ObjectId
    #      - Check inventory availability
    #      - Decrement inventory
    #    - Set order status = "paid"
    # 4. If outcome == "failure":
    #    - Set order status = "failed"
    # 5. If outcome == "canceled":
    #    - Set order status = "canceled"
    # 6. Save and return updated order
```

**Business Rules:**
- Only transitions from "pending" to final status
- If already finalized, returns without changes (idempotent)
- Inventory decremented ONLY on successful payment
- If insufficient inventory, marks order as "failed"

**Payment Flow:**
```
1. User creates order from cart (status="pending")
2. User pays (external payment gateway - not implemented)
3. Payment webhook/confirmation calls confirm() API
4. Inventory decremented + order status updated
```

---

### 6. Order Service (app/services/order_service.py)

**Responsibility:** Order retrieval and management

**Key Methods:**

```python
async def get_user_orders(user_id: str, skip=0, limit=20) -> list[Order]:
    # Get all orders for user (paginated)

async def get_order_by_id(order_id: str, user_id: str) -> Order:
    # 1. Get order by MongoDB ObjectId
    # 2. Verify order belongs to user (security check)
    # Raises HTTPException(404) if not found or unauthorized

async def get_all_orders(skip=0, limit=50) -> list[Order]:
    # Get all orders (admin only)
    # Paginated
```

---

## 🌐 API Layer

### Authentication Dependencies (app/api/deps.py)

```python
def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    # 1. Extract JWT token from Authorization header
    # 2. Decode and validate token
    # 3. Return payload: {"sub": user_id, "role": "user|admin"}
    # Raises HTTPException(401) if invalid/expired

def admin_required(user=Depends(get_current_user)):
    # 1. Call get_current_user()
    # 2. Check if role == "admin"
    # Raises HTTPException(403) if not admin
```

**Usage in Routes:**
```python
@router.get("/cart")
async def get_cart(user=Depends(get_current_user)):
    # user = {"sub": "507f...", "role": "user"}
    pass

@router.post("/admin/products")
async def create_product(_=Depends(admin_required)):
    # Only admins can access
    pass
```

---

### Service Dependencies (app/api/service_deps.py)

**Purpose:** Provide service instances via dependency injection

```python
def get_auth_service() -> AuthService:
    return AuthService()  # Creates new instance with default repositories

def get_product_service() -> ProductService:
    return ProductService()

# etc. for all services
```

**Usage in Routes:**
```python
@router.post("/auth/signup")
async def signup(
    data: SignupRequest, 
    auth_service: AuthService = Depends(get_auth_service)
):
    return await auth_service.signup_user(data.email, data.password)
```

**Benefits:**
- Easy to mock in tests
- Centralized service creation
- Clean separation of concerns

---

### Middleware (app/api/middleware.py)

**LoggingMiddleware:**
- Logs request method, path, client IP, user agent
- Measures and logs response time
- Adds `X-Process-Time` header to response
- Logs errors with stack traces

**Example Logs:**
```
→ Request: GET /products
  Client: 172.17.0.1
  User-Agent: Mozilla/5.0 ...
← Response: 200
  Duration: 0.045s
```

---

### Rate Limiting (app/api/rate_limit.py)

**Configuration:**
```python
PRODUCT_RATE_LIMIT = "5/minute"  # 5 requests per minute per IP
```

**Usage:**
```python
@router.get("")
@limiter.limit(PRODUCT_RATE_LIMIT)
async def list_products(request: Request, ...):
    # Rate limited to 5 req/min per IP
    pass
```

**Error Response (429):**
```json
{
  "error": "rate_limit_exceeded",
  "message": "Too many requests. Please slow down and try again later.",
  "detail": "5 per 1 minute"
}
```

---

### API Routers

#### 1. Auth Router (/auth)

**Endpoints:**

```python
POST /auth/signup
    Body: {"email": "...", "password": "..."}
    Returns: {"access_token": "...", "token_type": "bearer"}
    Public

POST /auth/login
    Body: {"email": "...", "password": "..."}
    Returns: {"access_token": "...", "token_type": "bearer"}
    Public

GET /auth/me
    Returns: {"id": "...", "email": "...", "role": "...", "created_at": "..."}
    Requires: Authentication

POST /auth/promote-to-admin
    Body: {"email": "..."}
    Returns: Updated user object
    Requires: Admin
```

---

#### 2. Product Router (/products)

**Endpoints:**

```python
GET /products?q={query}&skip={skip}&limit={limit}
    Query params:
        - q: Search query (optional)
        - skip: Pagination offset (default: 0)
        - limit: Page size (default: 20, max: 100)
    Returns: Array of products
    Public
    Rate limit: 5 req/min

GET /products/{slug}
    Path param: slug (e.g., "gaming-laptop-pro")
    Returns: Single product
    Public
    Rate limit: 5 req/min
```

---

#### 3. Cart Router (/cart)

**Endpoints:**

```python
GET /cart
    Returns: User's cart with items
    Requires: Authentication

POST /cart/add
    Body: {"product_id": 1, "qty": 2}
    Returns: Updated cart
    Requires: Authentication

POST /cart/remove
    Body: {"product_id": 1}
    Returns: Updated cart
    Requires: Authentication
```

---

#### 4. Checkout Router (/checkout)

**Endpoints:**

```python
POST /checkout/create-order
    Body: None (uses cart)
    Returns: {"order_id": "...", "status": "pending", "total": 123.45}
    Requires: Authentication
```

---

#### 5. Order Router (/orders)

**Endpoints:**

```python
GET /orders?skip={skip}&limit={limit}
    Query params: skip, limit
    Returns: Array of user's orders
    Requires: Authentication

GET /orders/{order_id}
    Path param: order_id (MongoDB ObjectId)
    Returns: Single order (if belongs to user)
    Requires: Authentication

GET /orders/admin/all?skip={skip}&limit={limit}
    Query params: skip, limit (max: 200)
    Returns: All orders in system
    Requires: Admin
```

---

#### 6. Payment Router (/payments)

**Endpoints:**

```python
POST /payments/confirm?order_id={order_id}&outcome={outcome}
    Query params:
        - order_id: MongoDB ObjectId string
        - outcome: "success" | "failure" | "canceled" (default: "success")
    Returns: {"order_id": "...", "status": "paid|failed|canceled"}
    Requires: Authentication (must own order)
```

---

#### 7. Admin Router (/admin)

**Endpoints:**

```python
POST /admin/products
    Body: ProductCreateRequest (all product fields)
    Returns: Created product with MongoDB id
    Requires: Admin

PATCH /admin/products/{product_id}
    Path param: product_id (MongoDB ObjectId)
    Body: ProductUpdateRequest (all product fields)
    Returns: Updated product
    Requires: Admin

DELETE /admin/products/{product_id}
    Path param: product_id (MongoDB ObjectId)
    Returns: Confirmation message
    Requires: Admin
```

---

## 🔐 Authentication & Security

### Authentication Flow

**1. User Signup/Login:**
```
Client → POST /auth/signup {"email", "password"}
       ← 200 {"access_token": "eyJ...", "token_type": "bearer"}
```

**2. Access Protected Endpoint:**
```
Client → GET /cart
         Headers: Authorization: Bearer eyJ...
       ← 200 {cart data}
```

**3. Token Validation:**
```python
1. FastAPI extracts token from Authorization header
2. get_current_user() dependency called
3. JWT decoded and validated
4. Expiration checked (15 min)
5. Payload returned: {"sub": user_id, "role": role}
6. Route handler receives user object
```

---

### Security Best Practices Implemented

✅ **Password Security:**
- Bcrypt hashing with automatic salt
- Never store plain text passwords
- Constant-time comparison via bcrypt

✅ **JWT Security:**
- Short token expiration (15 minutes)
- Secret key from environment variable
- Signature verification on every request

✅ **Authorization:**
- Role-based access control (user/admin)
- Order ownership verification
- Admin-only endpoints protected

✅ **Input Validation:**
- Pydantic schemas validate all inputs
- Email format validation
- Price/quantity validation (must be positive)

✅ **Rate Limiting:**
- IP-based rate limiting on product endpoints
- Prevents abuse and DDoS

✅ **CORS:**
- Configured allowed origins
- Credentials support for cookies
- Controlled methods and headers

---

### Security Improvements Needed for Production

⚠️ **High Priority:**
1. Change default JWT secret (use strong random key)
2. Change default admin credentials
3. Implement refresh tokens for longer sessions
4. Add HTTPS enforcement
5. Implement request signing for payment webhooks
6. Add CSRF protection for state-changing operations

⚠️ **Medium Priority:**
1. Implement account lockout after failed login attempts
2. Add email verification for signup
3. Implement password reset flow
4. Add audit logging for admin actions
5. Implement API key authentication for service-to-service calls

---

## 💾 Caching Strategy

### Cache Architecture

```
┌─────────────┐     Cache Hit      ┌───────────┐
│   Client    │ ←─────────────────  │   Redis   │
└─────────────┘                     └───────────┘
       │                                   ↑
       │ Cache Miss                        │
       ↓                                   │
┌─────────────┐                            │
│   Service   │ ───── Store Result ────────┘
└─────────────┘
       │
       ↓
┌─────────────┐
│   MongoDB   │
└─────────────┘
```

### Cached Operations

**Product Service:**
- `list_products()`: Cached by query parameters
  - Key: `ecommerce:products:list:q={query}:skip={skip}:limit={limit}`
  - TTL: 5 minutes
  
- `get_product_by_slug()`: Cached by slug
  - Key: `ecommerce:products:slug:{slug}`
  - TTL: 5 minutes

### Cache Invalidation Strategy

**Invalidation Triggers:**
- **Create Product**: Invalidate all list caches
- **Update Product**: Invalidate specific product + all list caches
- **Delete Product**: Invalidate specific product + all list caches

**Implementation:**
```python
# After product update
await invalidate_cache("products", f"slug:{old_slug}")
await invalidate_cache("products", "list:*")  # Wildcard pattern
```

### Performance Impact

**Without Cache (Database Query):**
- Average response time: 45-100ms
- Database load: High

**With Cache (Redis Hit):**
- Average response time: 2-5ms
- Database load: Minimal
- **Improvement: 10-20x faster**

---

## ⚙️ Configuration & Environment

### Environment Variables (.env)

```bash
# Database
MONGODB_URI=mongodb://localhost:27017/ecommerce

# JWT Authentication
JWT_SECRET=your-super-secret-key-change-this-in-production
JWT_ALG=HS256
ACCESS_TOKEN_EXPIRES_MIN=15

# Redis Cache
REDIS_URL=redis://localhost:6379
REDIS_ENABLED=true
CACHE_TTL_SECONDS=300

# Admin User (auto-created on startup)
CREATE_DEFAULT_ADMIN=true
DEFAULT_ADMIN_EMAIL=admin@example.com
DEFAULT_ADMIN_PASSWORD=admin123

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:8080
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=*
CORS_ALLOW_HEADERS=*

# Stripe (not currently used)
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=

# Environment
APP_ENV=dev
```

### Database Seeding

**On Application Startup:**

1. **Admin User Created:**
   - Email: `admin@example.com` (configurable)
   - Password: `admin123` (configurable)
   - Role: `admin`
   - ⚠️ Only created if doesn't exist

2. **20 Sample Products Created:**
   - **Electronics** (5): Laptop, headphones, TV, keyboard, smartphone
   - **Fashion** (5): Leather jacket, sunglasses, shoes, backpack, watch
   - **Home & Living** (5): Coffee maker, mattress, vacuum, air purifier, office chair
   - **Sports & Fitness** (5): Yoga mat, dumbbells, fitness tracker, protein powder, resistance bands
   - ⚠️ Only created if database is empty

**Product Examples:**
```python
{
    "product_id": 1,
    "name": "Gaming Laptop Pro",
    "slug": "gaming-laptop-pro",
    "description": "High-performance gaming laptop...",
    "price": 2499.99,
    "image": "https://images.unsplash.com/...",
    "inventory": 15,
    "category": "Electronics",
    "is_active": True
}
```

---

## 🧪 Testing Strategy

### Test Structure

```
tests/
├── conftest.py                    # Shared fixtures
├── test_auth_service.py           # Auth tests (signup, login, promote)
├── test_product_service.py        # Product tests (CRUD, search, cache)
├── test_cart_service.py           # Cart tests (add, remove, clear)
├── test_checkout_service.py       # Checkout tests (order creation)
├── test_order_service.py          # Order tests (retrieval, authorization)
└── test_payment_service.py        # Payment tests (mock processing)
```

### Testing Approach

**Unit Tests (Isolated):**
- Mock all dependencies (repositories, database, cache)
- Test business logic only
- Fast execution (no I/O)
- No real database or Redis required

**Test Fixtures (conftest.py):**

```python
# Factory fixtures for creating mock objects
mock_user_factory()       # Create mock users
mock_product_factory()    # Create mock products
mock_cart_factory()       # Create mock carts
mock_order_factory()      # Create mock orders
mock_cart_item_factory()  # Create cart items

# Example usage in tests
def test_signup(mock_user_factory):
    mock_user = mock_user_factory(email="test@example.com")
    # Use in test...
```

**Mock Strategy:**
```python
# Mock repository methods
@patch('app.repositories.user_repository.UserRepository.find_by_email')
@patch('app.repositories.user_repository.UserRepository.create')
async def test_signup(mock_create, mock_find_by_email, mock_user_factory):
    # Setup mocks
    mock_find_by_email.return_value = None  # User doesn't exist
    mock_user = mock_user_factory()
    mock_create.return_value = mock_user
    
    # Test service
    service = AuthService()
    result = await service.signup_user("test@example.com", "password123")
    
    # Assertions
    assert result["access_token"]
    assert result["token_type"] == "bearer"
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_auth_service.py

# Run with coverage
pytest --cov=app tests/

# Run with verbose output
pytest -v
```

---

## 🐳 Deployment & Docker

### Docker Compose Architecture

```yaml
services:
  mongo:
    image: mongo:6.0
    ports: ["27017:27017"]
    volumes: [mongo_data:/data/db]

  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]
    volumes: [redis_data:/data]
    command: redis-server --appendonly yes

  mongo-express:
    image: mongo-express:1
    ports: ["8081:8081"]
    environment:
      ME_CONFIG_BASICAUTH_USERNAME: admin
      ME_CONFIG_BASICAUTH_PASSWORD: admin

  api:
    build: .
    ports: ["8000:8000"]
    depends_on: [mongo, redis]
    volumes:
      - ./app:/app/app           # Hot reload
      - ./pyproject.toml:/app/pyproject.toml
    command: uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Dockerfile

```dockerfile
FROM python:3.11-slim

# Install uv package manager
RUN pip install --upgrade pip && pip install uv

WORKDIR /app

# Copy dependencies
COPY pyproject.toml ./

# Install dependencies
RUN uv sync --no-dev

# Activate virtual environment
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="/app/.venv/bin:$PATH"

# Copy source code
COPY app ./app

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Startup Commands

```bash
# Build and start all services
docker-compose up --build

# Start in detached mode
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Service URLs

- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **MongoDB**: localhost:27017
- **Mongo Express**: http://localhost:8081 (admin/admin)
- **Redis**: localhost:6379

---

## 📊 API Usage Examples

### 1. User Signup

```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass123"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

### 2. Login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "SecurePass123"
  }'
```

---

### 3. Get Current User

```bash
curl -X GET http://localhost:8000/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Response:**
```json
{
  "id": "507f1f77bcf86cd799439011",
  "email": "john@example.com",
  "role": "user",
  "created_at": "2024-10-21T10:30:00"
}
```

---

### 4. List Products

```bash
# All products
curl http://localhost:8000/products

# Search products
curl "http://localhost:8000/products?q=laptop&skip=0&limit=10"
```

---

### 5. Get Product by Slug

```bash
curl http://localhost:8000/products/gaming-laptop-pro
```

---

### 6. Add to Cart

```bash
curl -X POST http://localhost:8000/cart/add \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 1,
    "qty": 2
  }'
```

---

### 7. Get Cart

```bash
curl http://localhost:8000/cart \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Response:**
```json
{
  "_id": "507f1f77bcf86cd799439013",
  "user_id": "507f1f77bcf86cd799439011",
  "items": [
    {"product_id": 1, "qty": 2},
    {"product_id": 5, "qty": 1}
  ],
  "updated_at": "2024-10-21T10:35:00"
}
```

---

### 8. Create Order

```bash
curl -X POST http://localhost:8000/checkout/create-order \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Response:**
```json
{
  "order_id": "507f1f77bcf86cd799439014",
  "status": "pending",
  "total": 2999.98
}
```

---

### 9. Confirm Payment

```bash
curl -X POST "http://localhost:8000/payments/confirm?order_id=507f1f77bcf86cd799439014&outcome=success" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

**Response:**
```json
{
  "order_id": "507f1f77bcf86cd799439014",
  "status": "paid"
}
```

---

### 10. Get User Orders

```bash
curl http://localhost:8000/orders \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

### 11. Admin: Create Product

```bash
curl -X POST http://localhost:8000/admin/products \
  -H "Authorization: Bearer ADMIN_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 101,
    "name": "New Product",
    "slug": "new-product",
    "description": "Product description",
    "price": 99.99,
    "image": "https://example.com/image.jpg",
    "inventory": 50,
    "category": "Electronics",
    "is_active": true
  }'
```

---

### 12. Admin: Update Product

```bash
curl -X PATCH http://localhost:8000/admin/products/507f1f77bcf86cd799439012 \
  -H "Authorization: Bearer ADMIN_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 101,
    "name": "Updated Product Name",
    ...
  }'
```

---

### 13. Admin: Delete Product

```bash
curl -X DELETE http://localhost:8000/admin/products/507f1f77bcf86cd799439012 \
  -H "Authorization: Bearer ADMIN_TOKEN_HERE"
```

---

## 🔍 Common Issues & Solutions

### Issue 1: JWT Token Expired

**Symptom:** 401 Unauthorized error on protected endpoints

**Cause:** Token expires after 15 minutes

**Solution:** Login again to get new token

---

### Issue 2: Redis Connection Failed

**Symptom:** App starts but shows Redis connection error

**Cause:** Redis not running or wrong connection string

**Solution:**
1. Check Redis is running: `docker ps | grep redis`
2. Verify REDIS_URL in .env
3. App continues without cache (degraded mode)

---

### Issue 3: MongoDB Connection Failed

**Symptom:** App crashes on startup

**Cause:** MongoDB not running or wrong connection string

**Solution:**
1. Check MongoDB is running: `docker ps | grep mongo`
2. Verify MONGODB_URI in .env
3. Restart services: `docker-compose restart`

---

### Issue 4: Cart Shows Product IDs Only

**Expected Behavior:** Cart stores integer `product_id` (1, 2, 3...)

**Frontend Integration:** Fetch product details separately using product_id

**Example:**
```javascript
// Get cart
const cart = await fetch('/cart');
// cart.items = [{product_id: 1, qty: 2}]

// Fetch product details
for (const item of cart.items) {
  // Look up product by product_id (not by MongoDB _id)
  const product = await fetch(`/products?product_id=${item.product_id}`);
  // Display product.name, product.price, etc.
}
```

---

### Issue 5: Rate Limit Exceeded

**Symptom:** 429 error on product endpoints

**Cause:** Exceeded 5 requests per minute

**Solution:**
1. Wait 60 seconds
2. Reduce request frequency
3. Implement client-side caching
4. For development, increase limit in `rate_limit.py`

---

## 📝 Development Workflow

### 1. Add New Endpoint

**Steps:**
1. Create Pydantic schema in `app/schemas/`
2. Add method to service in `app/services/`
3. Add route to router in `app/api/routers/`
4. Add service dependency to `app/api/service_deps.py` (if new service)
5. Include router in `app/main.py` (if new router)
6. Write tests in `tests/`

---

### 2. Add New Database Model

**Steps:**
1. Create model in `app/db/models/`
2. Add to `init_beanie()` in `app/db/init.py`
3. Create repository in `app/repositories/`
4. Create service in `app/services/`
5. Add test fixtures in `tests/conftest.py`

---

### 3. Add Caching to Endpoint

**Steps:**
1. Import decorator: `from app.core.cache_decorator import cached`
2. Add decorator to service method:
   ```python
   @cached(
       namespace="my_namespace",
       key_builder=lambda self, arg1, arg2: f"key:{arg1}:{arg2}"
   )
   async def my_method(self, arg1, arg2):
       pass
   ```
3. Add cache invalidation on mutations:
   ```python
   await invalidate_cache("my_namespace", "key:*")
   ```

---

## 🚀 Production Deployment Checklist

### Pre-Deployment

- [ ] Change JWT_SECRET to strong random value
- [ ] Change default admin password
- [ ] Set APP_ENV=production
- [ ] Configure production MongoDB URI
- [ ] Configure production Redis URI
- [ ] Enable HTTPS/TLS
- [ ] Review and restrict CORS_ORIGINS
- [ ] Set up monitoring and alerting
- [ ] Configure backup strategy for MongoDB
- [ ] Set up logging aggregation
- [ ] Implement rate limiting on all endpoints
- [ ] Add request signing for webhooks
- [ ] Set up health check endpoints
- [ ] Configure auto-scaling rules
- [ ] Set up CI/CD pipeline
- [ ] Perform security audit
- [ ] Load testing

### Post-Deployment

- [ ] Monitor error rates
- [ ] Monitor response times
- [ ] Monitor cache hit rates
- [ ] Monitor database performance
- [ ] Set up alerts for high error rates
- [ ] Set up alerts for high response times
- [ ] Review and rotate secrets regularly
- [ ] Monitor rate limit violations
- [ ] Review admin action logs

---

## 📚 Additional Resources

### Documentation Files in Project

- `README.md` - Main project documentation
- `REDIS_CACHING_GUIDE.md` - Redis caching best practices
- `AUTO_REFRESH_GUIDE.md` - Auto-refresh development setup
- `CONFIG_FILES_EXPLAINED.md` - Configuration file explanations
- `DOCKER_REDIS_SETUP.md` - Docker and Redis setup guide
- `TESTING_GUIDE.md` - Testing guide and best practices
- `tests/TEST_SUMMARY.md` - Test coverage summary

### Code Explanation Files

- `app/core/config_EXPLAINED.py` - Configuration deep dive
- `app/core/service_decorator_EXPLAINED.py` - Service decorator explanation
- `app/db/init_EXPLAINED.py` - Database initialization explanation
- `app/repositories/cart_repository_EXPLAINED.py` - Cart repository deep dive
- `app/repositories/product_repository_EXPLAINED.py` - Product repository deep dive
- `app/services/cart_service_EXPLAINED.py` - Cart service business logic
- `app/services/product_service_EXPLAINED.py` - Product service with caching
- `app/api/routers/admin_router_EXPLAINED.py` - Admin endpoints explanation
- `app/api/routers/product_router_EXPLAINED.py` - Product endpoints explanation
- `app/db/models/cart_EXPLAINED.py` - Cart model explanation
- `app/db/models/order_EXPLAINED.py` - Order model explanation
- `app/db/models/product_EXPLAINED.py` - Product model explanation
- `app/db/models/user_EXPLAINED.py` - User model explanation

---

## 🎓 Key Learning Points

### Architecture Lessons

1. **Layered Architecture**: Clean separation between API, service, repository, and database layers
2. **Dependency Injection**: Services and repositories injected, making code testable
3. **Repository Pattern**: Abstracts database operations
4. **Service Pattern**: Encapsulates business logic
5. **Caching Strategy**: Redis for performance, automatic invalidation

### FastAPI Best Practices

1. **Pydantic Schemas**: Type-safe request/response validation
2. **Dependency Injection**: Built-in DI system for clean code
3. **Async/Await**: Full async support for high performance
4. **OpenAPI Documentation**: Automatic interactive docs
5. **Middleware**: Custom logging and processing

### MongoDB with Beanie

1. **Async ODM**: Full async support for MongoDB
2. **Pydantic Integration**: Models are Pydantic models
3. **Indexing**: Strategic indexes for query performance
4. **Embedded Documents**: CartItem, OrderItem as embedded schemas

### Security Implementation

1. **JWT Tokens**: Stateless authentication with expiration
2. **Password Hashing**: Bcrypt with automatic salting
3. **Role-Based Access**: User/admin roles
4. **Input Validation**: Pydantic ensures type safety
5. **Rate Limiting**: Prevent abuse

---

## 📞 Support & Contact

For issues or questions about this codebase:
1. Review this PROJECT_CONTEXT.md file
2. Check code explanation files in the project
3. Review test files for usage examples
4. Check API documentation at /docs endpoint

---

**End of Project Context Document**

*This document represents the complete state of the e-commerce-python-training project as of 2025-11-04. Use this as a reference for understanding the codebase, making changes, or onboarding new developers.*

