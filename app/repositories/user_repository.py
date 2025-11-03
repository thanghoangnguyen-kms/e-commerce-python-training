"""
User repository for user-related data access operations.
"""
from app.repositories.base_repository import BaseRepository
from app.db.models.user import User


class UserRepository(BaseRepository[User]):
    """Repository for User model operations."""

    def __init__(self):
        super().__init__(User)

    async def find_by_email(self, email: str) -> User | None:
        """Find a user by email address."""
        return await self.find_one(User.email == email)

    async def email_exists(self, email: str) -> bool:
        """Check if a user with the given email exists."""
        user = await self.find_by_email(email)
        return user is not None
