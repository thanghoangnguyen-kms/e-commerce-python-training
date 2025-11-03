from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
import logging

from app.db.models.user import User
from app.db.models.product import Product
from app.db.models.cart import Cart
from app.db.models.order import Order
from app.db.seed import seed_database

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Singleton manager for MongoDB connection.
    Handles database initialization and cleanup.
    """
    _instance: 'DatabaseManager | None' = None
    _client: AsyncIOMotorClient | None = None
    _is_initialized: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def initialize(self, mongo_uri: str) -> None:
        """
        Initialize MongoDB connection and Beanie ODM.
        
        Args:
            mongo_uri: MongoDB connection string
            
        Raises:
            Exception: If connection or initialization fails
        """
        if self._is_initialized:
            logger.warning("Database already initialized, skipping...")
            return

        try:
            logger.info("Initializing MongoDB connection...")
            self._client = AsyncIOMotorClient(mongo_uri)
            
            # Test connection
            await self._client.admin.command('ping')
            logger.info("MongoDB connection successful")
            
            # Get database from connection string or use default
            db = self._client.get_default_database()
            
            # Initialize Beanie with all document models
            await init_beanie(
                database=db,
                document_models=[User, Product, Cart, Order]
            )
            logger.info("Beanie ODM initialized successfully")
            
            # Seed database with initial data
            await seed_database()
            logger.info("Database seeding completed")
            
            self._is_initialized = True
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            if self._client:
                self._client.close()
                self._client = None
            raise

    async def close(self) -> None:
        """
        Close MongoDB connection gracefully.
        """
        if self._client:
            logger.info("Closing MongoDB connection...")
            self._client.close()
            self._client = None
            self._is_initialized = False
            logger.info("MongoDB connection closed")

    @property
    def is_initialized(self) -> bool:
        """Check if database is initialized."""
        return self._is_initialized

    @property
    def client(self) -> AsyncIOMotorClient | None:
        """Get the MongoDB client instance (use sparingly, prefer Beanie models)."""
        return self._client


# Global instance for easy access
db_manager = DatabaseManager()



async def get_database():
    """
    Dependency for getting database instance.
    Can be used in routes if direct DB access is needed.
    """
    if not db_manager.is_initialized:
        raise RuntimeError("Database not initialized")
    return db_manager.client.get_default_database()
