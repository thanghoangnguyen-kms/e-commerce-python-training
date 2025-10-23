# 🛍️ E-Commerce API

A modern, production-ready REST API for e-commerce applications built with FastAPI, MongoDB, and Beanie ODM.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-6.0+-green.svg)](https://www.mongodb.com/)

## ✨ Features

- 🔐 **JWT Authentication** - Secure token-based authentication with role-based access control
- 👥 **User Management** - User registration, login, and profile management
- 🛒 **Shopping Cart** - Add, remove, and manage cart items
- 📦 **Product Catalog** - Browse, search, and filter products by category
- 💳 **Order Processing** - Create orders from cart with inventory management
- 💰 **Payment Integration** - Mock payment system ready for real gateway integration (Stripe-ready)
- 👨‍💼 **Admin Panel** - Admin-only endpoints for product and order management
- 📊 **Comprehensive Logging** - Request/response logging middleware
- 🐳 **Docker Support** - Fully containerized with Docker Compose
- 📚 **Auto-generated API Docs** - Interactive Swagger UI and ReDoc

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

- **Framework:** FastAPI 0.115+
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

5. **Access the application:**
   - API: http://localhost:8000
   - Interactive API Docs: http://localhost:8000/docs
   - ReDoc Documentation: http://localhost:8000/redoc
   - Mongo Express (DB UI): http://localhost:8081

## 📖 API Documentation

### Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/auth/signup` | Register new user | No |
| POST | `/auth/login` | Login and get JWT tokens | No |
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

2. **Use the access token:**
   ```bash
   curl http://localhost:8000/auth/me \
     -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
   ```

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
# Database
MONGODB_URI=mongodb://mongo:27017/ecommerce

# JWT Configuration
JWT_SECRET=your-secret-key-here
JWT_ALG=HS256
ACCESS_TOKEN_EXPIRES_MIN=15
REFRESH_TOKEN_EXPIRES_MIN=1440

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
├── docs/                        # Documentation
├── docker-compose.yml           # Docker services
├── Dockerfile                   # API container
├── pyproject.toml               # Python dependencies
├── .env                         # Environment variables (not in git)
├── .env.example                 # Environment template
└── README.md                    # This file
```

## 🚢 Deployment

### Production Checklist

Before deploying to production:

- [ ] Generate strong JWT secret
- [ ] Change default admin credentials
- [ ] Set `CREATE_DEFAULT_ADMIN=false`
- [ ] Set `APP_ENV=prod`
- [ ] Disable Mongo Express (don't start in production)
- [ ] Enable MongoDB authentication
- [ ] Set up HTTPS/SSL certificates
- [ ] Configure CORS for your frontend domain
- [ ] Set up proper logging and monitoring
- [ ] Review and restrict firewall rules

### Docker Production

```bash
# Build and start
docker-compose up -d api mongo

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

### Environment Variables for Production

```env
MONGODB_URI=mongodb://username:password@your-mongodb-host:27017/ecommerce
JWT_SECRET=<strong-random-secret-minimum-32-chars>
APP_ENV=prod
CREATE_DEFAULT_ADMIN=false
```

## 🛡️ Security

- ✅ Passwords hashed with bcrypt
- ✅ JWT tokens with expiration
- ✅ Role-based access control (RBAC)
- ✅ Environment variables for sensitive data
- ✅ Input validation with Pydantic
- ✅ Protected admin endpoints

## 📋 TODO

- [ ] **Unit Tests** - Add comprehensive test coverage
- [ ] **Rate Limiting** - Implement API rate limiting to prevent abuse
- [ ] **CORS** - Configure CORS for production frontend integration

## 📄 License

This project is licensed under the MIT License.
