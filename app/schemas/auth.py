"""Authentication request/response schemas."""
from pydantic import BaseModel, EmailStr, Field


class SignupRequest(BaseModel):
    """Request schema for user signup."""
    email: EmailStr = Field(..., example="user@example.com", description="User email address")
    password: str = Field(..., min_length=6, example="SecurePass123", description="User password (min 6 characters)")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "john.doe@example.com",
                    "password": "MySecurePassword123"
                }
            ]
        }
    }


class LoginRequest(SignupRequest):
    """Request schema for user login."""
    pass


class TokenResponse(BaseModel):
    """Response schema for authentication tokens."""
    access_token: str = Field(..., example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
    refresh_token: str = Field(..., example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
    token_type: str = Field(default="bearer", example="bearer")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NzE2YTJiZjhmYzQ4ZjAwMDE2ZDMyNGEiLCJyb2xlIjoidXNlciIsImlhdCI6MTcyOTUzNjE5MSwiZXhwIjoxNzI5NTM3MDkxfQ.xyz",
                    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2NzE2YTJiZjhmYzQ4ZjAwMDE2ZDMyNGEiLCJyb2xlIjoidXNlciIsImlhdCI6MTcyOTUzNjE5MSwiZXhwIjoxNzI5NjIyNTkxfQ.abc",
                    "token_type": "bearer"
                }
            ]
        }
    }


class UserResponse(BaseModel):
    """Response schema for user information."""
    id: str = Field(..., example="67123abc456def789012345")
    email: EmailStr = Field(..., example="user@example.com")
    role: str = Field(..., example="user")
    created_at: str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "67123abc456def789012345",
                    "email": "john.doe@example.com",
                    "role": "admin",
                    "created_at": "2024-10-21T10:30:00"
                }
            ]
        }
    }


class PromoteUserRequest(BaseModel):
    """Request schema for promoting user to admin."""
    email: EmailStr = Field(..., example="user@example.com", description="Email of user to promote to admin")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "email": "john.doe@example.com"
                }
            ]
        }
    }

