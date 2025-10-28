# 🛍️ E-Commerce API

A modern, production-ready REST API for e-commerce applications built with FastAPI, MongoDB, and Beanie ODM.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-6.0+-green.svg)](https://www.mongodb.com/)

## ✨ Features

- 🔐 **JWT Authentication** - Secure token-based authentication with role-based access control (access tokens expire in 15 minutes)
- 👥 **User Management** - User registration, login, and profile management
- 🛒 **Shopping Cart** - Add, remove, and manage cart items
- 📦 **Product Catalog** - Browse, search, and filter products by category
- 👨‍💼 **Admin Panel** - Admin-only endpoints for product and order management
- 📊 **Comprehensive Logging** - Request/response logging middleware
- 🌐 **CORS Support** - Configured for frontend integration (React, Vue, Vite) in the future.
- 🐳 **Docker Support** - Fully containerized with Docker Compose

## 🏗️ Architecture
The project follows a clean, layered architecture:

```
app/
├── api/              # API layer (routes, dependencies, middleware)
├── core/             # Core functionality (config, security, JWT)
├── db/               # Database layer (models, initialization, seeding)
├── schemas/          # Pydantic schemas for request/response validation
├── services/         # Business logic layer
└── scripts/          # Utility scripts (admin creation, etc.)
```

### Tech Stack
- **Cache:** Redis 7.0+ for high-performance caching

- **Framework:** FastAPI 0.115+
- **Rate Limiting:** slowapi (IP-based rate limiting)
- **Database:** MongoDB 6.0+ with Beanie ODM
- **Authentication:** JWT (PyJWT) + bcrypt
- **Validation:** Pydantic v2
- **Server:** Uvicorn with hot reload
- **Package Manager:** uv (fast Python package installer)

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- Docker & Docker Compose

### Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd e-commerce
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   ```

3. **Generate a strong JWT secret:**
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```
   Update `JWT_SECRET` in `.env` with the generated value.

4. **Start the application with Docker:**
   ```bash
   docker-compose up --build
   ```

   - Redis: localhost:6379
5. **Access the application:**
   - API: http://localhost:8000
   - Interactive API Docs: http://localhost:8000/docs
   - ReDoc Documentation: http://localhost:8000/redoc
   - Mongo Express (DB UI): http://localhost:8081

## 📖 API Documentation

### Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/auth/signup` | Register new user and get access token (15 min expiry) | No |
| POST | `/auth/login` | Login and get access token (15 min expiry) | No |
| GET | `/auth/me` | Get current user info | Yes |
| POST | `/auth/promote-to-admin` | Promote user to admin | Admin only |

### Product Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/products` | List all products | No |
| GET | `/products?q={query}` | Search products | No |
| GET | `/products/{slug}` | Get product by slug | No |

### Cart Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/cart` | Get user's cart | Yes |
| POST | `/cart/add` | Add item to cart | Yes |
| POST | `/cart/remove` | Remove item from cart | Yes |

### Order Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/checkout/create-order` | Create order from cart | Yes |
| GET | `/orders` | Get user's orders | Yes |
| GET | `/orders/{id}` | Get specific order | Yes |
| GET | `/orders/admin/all` | Get all orders | Admin only |

### Admin Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/admin/products` | Create new product | Admin only |
| PATCH | `/admin/products/{id}` | Update product | Admin only |

### Payment Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/payments/confirm` | Confirm payment (mock) | Yes |

## 🔐 Authentication

This API uses **JWT (JSON Web Token)** authentication with access tokens that expire after 15 minutes for enhanced security.

### Getting Started

1. **Sign up for an account:**
   ```bash
   curl -X POST http://localhost:8000/auth/signup \
     -H "Content-Type: application/json" \
     -d '{
       "email": "user@example.com",
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

2. **Use the access token:**
   ```bash
   curl http://localhost:8000/auth/me \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
   ```

3. **Token Expiration:**
   - Access tokens expire after **15 minutes**
   - After expiration, users must login again to get a new token
   - This enhances security by limiting the exposure window of stolen tokens

### Default Admin Account

On first startup, a default admin account is created:
- **Email:** admin@example.com
- **Password:** admin123

⚠️ **IMPORTANT:** Change these credentials immediately in production!

```bash
# Create a custom admin
python -m app.scripts.create_admin \
  --email admin@yourcompany.com \
  --password YourStrongPassword123!
```

## 🗄️ Database

### Seeded Data

The application automatically seeds the database with:
- 1 default admin user
- 20 sample products across 4 categories:
  - Electronics (5 products)
  - Fashion (5 products)
  - Home & Living (5 products)
  - Sports & Fitness (5 products)

### MongoDB Access

**Mongo Express UI:**
- URL: http://localhost:8081
- Username: admin
- Password: SecureMongoUI2024! (configured in `.env`)

**Direct MongoDB Connection:**
```bash
docker-compose exec mongo mongosh ecommerce
```

### Data Models

- **User:** Email, hashed password, role (user/admin)
- **Product:** ID, name, slug, description, price, image, inventory, category
- **Cart:** User ID, list of cart items (product ID, quantity)
- **Order:** User ID, list of order items, total, status, timestamps

## 🔧 Configuration

All configuration is managed through environment variables in `.env`:

```env
# Redis Cache
REDIS_URL=redis://redis:6379/0
CACHE_ENABLED=true
CACHE_TTL_SECONDS=300

# Database
MONGODB_URI=mongodb://mongo:27017/ecommerce

# JWT Configuration
JWT_SECRET=your-secret-key-here
# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=100

JWT_ALG=HS256
ACCESS_TOKEN_EXPIRES_MIN=15

# CORS Configuration (comma-separated origins)
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:8080
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=*
CORS_ALLOW_HEADERS=*

# Admin Defaults
DEFAULT_ADMIN_EMAIL=admin@example.com
DEFAULT_ADMIN_PASSWORD=admin123
CREATE_DEFAULT_ADMIN=true

# Mongo Express
MONGO_EXPRESS_USER=admin
MONGO_EXPRESS_PASSWORD=SecureMongoUI2024!

# Stripe (optional)
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=

# Environment
APP_ENV=dev
```

### CORS Configuration

The API is pre-configured to allow requests from common frontend development ports:
- **Port 3000** - React (Create React App), Next.js
- **Port 5173** - Vite (Vue, React, Svelte)
- **Port 8080** - Vue CLI

To customize allowed origins for your frontend:
```env
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
```

## 📝 Project Structure

```
e-commerce/
├── app/
│   ├── api/
│   │   ├── deps.py              # Dependencies (auth, DB)
│   │   ├── middleware.py        # Custom middleware
│   │   └── routers/             # API route handlers
│   ├── core/
│   │   ├── config.py            # Configuration management
│   │   ├── jwt.py               # JWT token operations
│   │   └── security.py          # Password hashing
│   ├── db/
│   │   ├── init.py              # Database initialization
│   │   ├── seed.py              # Data seeding
│   │   └── models/              # Beanie ODM models
│   ├── schemas/                 # Pydantic schemas
│   ├── services/                # Business logic
│   ├── scripts/                 # CLI scripts
│   └── main.py                  # Application entry point
├── tests/
│   ├── conftest.py              # Test fixtures and configuration
│   ├── test_auth.py             # Auth service tests
│   ├── test_cart.py             # Cart service tests
│   ├── test_checkout_orders.py  # Checkout service tests
│   ├── test_orders.py           # Order service tests
│   ├── test_payments.py         # Payment service tests
│   └── test_products.py         # Product service tests
├── docs/                        # Documentation
├── docker-compose.yml           # Docker services
├── Dockerfile                   # API container
├── pyproject.toml               # Python dependencies
├── pytest.ini                   # Pytest configuration
├── .env                         # Environment variables (not in git)
├── .env.example                 # Environment template
└── README.md                    # This file
```

## 🧪 Testing

This project includes comprehensive unit tests for all service layer business logic.

### Running Tests

**Run all tests:**
```bash
pytest tests/ -v
```

**Run specific test file:**
```bash
pytest tests/test_products.py -v
```

**Run specific test:**
```bash
pytest tests/test_products.py::TestProductService::test_create_product_success -v
```

**Run with coverage:**
```bash
pytest tests/ --cov=app --cov-report=html
- ✅ **AuthService** (8 tests)

### Test Coverage

  - Error handling (duplicate email, invalid credentials)

- ✅ **ProductService** (8 tests)
  - Product listing and search with caching
  - Product retrieval by slug/ID
  - Product creation with duplicate validation
  - Cache-aware operations

- ✅ **CartService** (8 tests)
  - Product listing and search
  - Product creation and updates
  - Duplicate validation
  - Inventory management

- ✅ **CheckoutService** (5 tests)
  - Cart creation and retrieval
  - Total calculation with multiple items
  - Quantity validation
  - Product availability checks

- ✅ **OrderService** (5 tests)
  - Order creation from cart
  - Order ownership validation (authorization)
  - Inventory validation
  - Error handling (not found, forbidden)

- ✅ **PaymentService** (6 tests)
  - Payment confirmation with status transitions
  - Order ownership validation
  - Admin order access
  - Failure scenarios (insufficient inventory, missing product)

**Total: 40 unit tests** covering all critical business logic paths with 100% service layer coverage.
  - Payment confirmation
  - Inventory decrement
  - Idempotency handling
  - Partial failure scenarios

**Total: 60 unit tests** covering all critical business logic paths.
```

### Environment Variables for Production

```env
MONGODB_URI=mongodb://username:password@your-mongodb-host:27017/ecommerce
JWT_SECRET=<strong-random-secret-minimum-32-chars>
APP_ENV=prod
CREATE_DEFAULT_ADMIN=false
```

## 🛡️ Security

CACHE_ENABLED=true
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=5
- ✅ Passwords hashed with bcrypt
- ✅ JWT tokens with 15-minute expiration
- ✅ Role-based access control (RBAC)
- ✅ Environment variables for sensitive data
- ✅ Input validation with Pydantic
- ✅ Protected admin endpoints
- ✅ CORS configured for secure cross-origin requests

### Security Best Practices

**Token Expiration:**
- Access tokens expire after 15 minutes
- Users must re-authenticate after expiration
- This minimizes the risk window if a token is compromised

**Password Security:**
- All passwords are hashed using bcrypt
- Never store plain-text passwords
**Rate Limiting:**
- API rate limiting prevents abuse (100 requests per minute per IP)
- Customizable limits per endpoint
- Automatic HTTP 429 response when limit exceeded
- Change default admin credentials in production


## 📄 License

This project is licensed under the MIT License.
