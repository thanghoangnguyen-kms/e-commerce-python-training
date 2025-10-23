from app.db.models.user import User
from app.core.security import hash_password, verify_password
from app.core.jwt import create_token
from app.core.config import settings
from fastapi import HTTPException


class AuthService:
    """
    Service layer for authentication operations.
    Handles user signup, login, and role management.
    """

    @staticmethod
    async def signup_user(email: str, password: str) -> dict:
        """
        Register a new user.
        Returns JWT tokens.
        """
        # Check if user already exists
        existing_user = await User.find_one(User.email == email)
        if existing_user:
            raise HTTPException(400, "Email already registered")

        # Create new user
        user = User(email=email, hashed_password=hash_password(password))
        await user.insert()

        # Generate tokens
        return {
            "access_token": create_token(str(user.id), user.role, settings.access_exp_min),
            "refresh_token": create_token(str(user.id), user.role, settings.refresh_exp_min),
            "token_type": "bearer"
        }

    @staticmethod
    async def login_user(email: str, password: str) -> dict:
        """
        Authenticate a user.
        Returns JWT tokens if credentials are valid.
        """
        user = await User.find_one(User.email == email)

        # Validate credentials
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(401, "Invalid credentials")

        # Generate tokens
        return {
            "access_token": create_token(str(user.id), user.role, settings.access_exp_min),
            "refresh_token": create_token(str(user.id), user.role, settings.refresh_exp_min),
            "token_type": "bearer"
        }

    @staticmethod
    async def get_user_by_id(user_id: str) -> User:
        """Get user by ID."""
        user = await User.get(user_id)
        if not user:
            raise HTTPException(404, "User not found")
        return user

    @staticmethod
    async def promote_user_to_admin(email: str) -> User:
        """
        Promote a user to admin role.
        Returns the updated user.
        """
        user = await User.find_one(User.email == email)
        if not user:
            raise HTTPException(404, "User not found")

        if user.role == "admin":
            raise HTTPException(400, "User is already an admin")

        user.role = "admin"
        await user.save()
        return user

