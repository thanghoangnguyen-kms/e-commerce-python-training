"""Authentication service for user signup, login, and role management."""
from app.db.models.user import User
from app.repositories.user_repository import UserRepository
from app.core.security import hash_password, verify_password
from app.core.jwt import create_token
from app.core.config import settings
from app.core.service_decorator import service_method
from fastapi import HTTPException


class AuthService:
    """
    Service layer for authentication operations.
    Handles user signup, login, and role management with JWT tokens.
    """

    def __init__(self, user_repository: UserRepository = None):
        """Initialize AuthService with repository dependency."""
        self.user_repository = user_repository or UserRepository()

    @service_method
    async def signup_user(self, email: str, password: str) -> dict:
        """
        Register a new user.

        Args:
            email: User's email address
            password: User's password (will be hashed)

        Returns:
            Dictionary with access_token and token_type

        Raises:
            HTTPException: If email already registered
        """
        # Check if user already exists
        existing_user = await self.user_repository.find_by_email(email)
        if existing_user:
            raise HTTPException(400, "Email already registered")

        # Create new user
        hashed_pw = hash_password(password)
        user = User(email=email, hashed_password=hashed_pw)
        created_user = await self.user_repository.create(user)

        # Generate access token (expires in 15 minutes)
        return {
            "access_token": create_token(str(created_user.id), created_user.role, settings.access_exp_min),
            "token_type": "bearer"
        }

    @service_method
    async def login_user(self, email: str, password: str) -> dict:
        """
        Authenticate a user.

        Args:
            email: User's email address
            password: User's password

        Returns:
            Dictionary with access_token and token_type

        Raises:
            HTTPException: If credentials are invalid
        """
        user = await self.user_repository.find_by_email(email)

        # Validate credentials
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(401, "Invalid credentials")

        # Generate access token (expires in 15 minutes)
        return {
            "access_token": create_token(str(user.id), user.role, settings.access_exp_min),
            "token_type": "bearer"
        }

    @service_method
    async def get_user_by_id(self, user_id: str) -> User:
        """
        Get user by ID.

        Args:
            user_id: User's MongoDB ObjectId string

        Returns:
            User model object

        Raises:
            HTTPException: If user not found
        """
        user = await self.user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(404, "User not found")
        return user

    @service_method
    async def promote_user_to_admin(self, email: str) -> User:
        """
        Promote a user to admin role.

        Args:
            email: Email of user to promote

        Returns:
            Updated User model object

        Raises:
            HTTPException: If user not found or already admin
        """
        user = await self.user_repository.find_by_email(email)
        if not user:
            raise HTTPException(404, "User not found")

        if user.role == "admin":
            raise HTTPException(400, "User is already an admin")

        user.role = "admin"
        await self.user_repository.update(user)
        return user
