from pydantic import BaseModel
import os

class Settings(BaseModel):
    mongodb_uri: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017/ecommerce")
    jwt_secret: str = os.getenv("JWT_SECRET", "change_me")
    jwt_alg: str = os.getenv("JWT_ALG", "HS256")
    access_exp_min: int = int(os.getenv("ACCESS_TOKEN_EXPIRES_MIN", "15"))
    refresh_exp_min: int = int(os.getenv("REFRESH_TOKEN_EXPIRES_MIN", "1440"))
    stripe_secret_key: str = os.getenv("STRIPE_SECRET_KEY", "")
    stripe_webhook_secret: str = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    app_env: str = os.getenv("APP_ENV", "dev")

    # Admin user configuration
    create_default_admin: bool = os.getenv("CREATE_DEFAULT_ADMIN", "true").lower() in ("true", "1", "yes")
    default_admin_email: str = os.getenv("DEFAULT_ADMIN_EMAIL", "admin@example.com")
    default_admin_password: str = os.getenv("DEFAULT_ADMIN_PASSWORD", "admin123")

settings = Settings()
