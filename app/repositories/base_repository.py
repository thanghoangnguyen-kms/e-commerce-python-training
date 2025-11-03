"""
Base repository pattern for common CRUD operations.
"""
from typing import Generic, TypeVar, Type
from beanie import Document

T = TypeVar("T", bound=Document)


class BaseRepository(Generic[T]):
    """
    Generic repository providing common CRUD operations.
    All repositories should inherit from this class.
    """

    def __init__(self, model: Type[T]):
        self.model = model

    async def get_by_id(self, id: str) -> T | None:
        """Get a document by its ID."""
        return await self.model.get(id)

    async def find_one(self, *args, **kwargs) -> T | None:
        """Find a single document matching the criteria."""
        return await self.model.find_one(*args, **kwargs)

    async def find_many(self, *args, skip: int = 0, limit: int = 100, **kwargs) -> list[T]:
        """Find multiple documents matching the criteria."""
        return await self.model.find(*args, **kwargs).skip(skip).limit(limit).to_list()

    async def find_all(self, skip: int = 0, limit: int = 100) -> list[T]:
        """Get all documents with pagination."""
        return await self.model.find().skip(skip).limit(limit).to_list()

    async def create(self, document: T) -> T:
        """Insert a new document."""
        await document.insert()
        return document

    async def update(self, document: T) -> T:
        """Update an existing document."""
        await document.save()
        return document

    async def delete(self, document: T) -> None:
        """Delete a document."""
        await document.delete()

    async def count(self, *args, **kwargs) -> int:
        """Count documents matching the criteria."""
        return await self.model.find(*args, **kwargs).count()
