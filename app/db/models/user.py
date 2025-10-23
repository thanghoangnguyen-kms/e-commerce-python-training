from beanie import Document, Indexed
from pydantic import BaseModel, EmailStr
from datetime import datetime

class User(Document):
    email: Indexed(EmailStr, unique=True)  # type: ignore
    hashed_password: str
    role: str = "user"  # "user" | "admin"
    created_at: datetime = datetime.utcnow()

    class Settings:
        name = "users"
