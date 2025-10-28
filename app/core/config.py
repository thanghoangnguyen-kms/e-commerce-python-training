from pydantic import BaseModel
import os

class Settings(BaseModel):
    mongodb_uri: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017/ecommerce")
    jwt_secret: str = os.getenv("JWT_SECRET", "change_me")
    jwt_alg: str = os.getenv("JWT_ALG", "HS256")
    access_exp_min: int = int(os.getenv("ACCESS_TOKEN_EXPIRES_MIN", "15"))
    stripe_secret_key: str = os.getenv("STRIPE_SECRET_KEY", "")
    stripe_webhook_secret: str = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    app_env: str = os.getenv("APP_ENV", "dev")

    # Redis configuration
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    redis_enabled: bool = os.getenv("REDIS_ENABLED", "true").lower() in ("true", "1", "yes")
    cache_ttl_seconds: int = int(os.getenv("CACHE_TTL_SECONDS", "300"))  # 5 minutes default

    # Admin user configuration
    create_default_admin: bool = os.getenv("CREATE_DEFAULT_ADMIN", "true").lower() in ("true", "1", "yes")
    default_admin_email: str = os.getenv("DEFAULT_ADMIN_EMAIL", "admin@example.com")
    default_admin_password: str = os.getenv("DEFAULT_ADMIN_PASSWORD", "admin123")

    # CORS configuration
    # Default allows common frontend dev ports: 3000 (React/Next), 5173 (Vite), 8080 (Vue CLI)
    cors_origins: str = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173,http://localhost:8080")
    cors_allow_credentials: bool = os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() in ("true", "1", "yes")
    cors_allow_methods: str = os.getenv("CORS_ALLOW_METHODS", "*")
    cors_allow_headers: str = os.getenv("CORS_ALLOW_HEADERS", "*")

    @property
    def cors_origins_list(self) -> list[str]:
        """Convert comma-separated CORS origins string to list."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

settings = Settings()
