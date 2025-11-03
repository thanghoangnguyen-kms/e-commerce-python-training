"""
Product repository for product-related data access operations.
"""
from app.repositories.base_repository import BaseRepository
from app.db.models.product import Product


class ProductRepository(BaseRepository[Product]):
    """Repository for Product model operations."""

    def __init__(self):
        super().__init__(Product)

    async def find_by_slug(self, slug: str, active_only: bool = True) -> Product | None:
        """Find a product by its slug."""
        if active_only:
            return await self.find_one(Product.slug == slug, Product.is_active == True)
        return await self.find_one(Product.slug == slug)

    async def find_by_product_id(self, product_id: int) -> Product | None:
        """Find a product by its product_id."""
        return await self.find_one(Product.product_id == product_id)

    async def search_products(
        self, 
        search_query: str | None = None, 
        skip: int = 0, 
        limit: int = 20
    ) -> list[Product]:
        """Search products by name or category."""
        if search_query:
            query = {
                "$or": [
                    {"name": {"$regex": search_query, "$options": "i"}},
                    {"category": {"$regex": search_query, "$options": "i"}}
                ]
            }
            return await self.find_many(query, skip=skip, limit=limit)
        return await self.find_all(skip=skip, limit=limit)

    async def decrement_inventory(self, product_id: str, quantity: int) -> Product | None:
        """Decrement product inventory by the specified quantity."""
        product = await self.get_by_id(product_id)
        if product and product.inventory >= quantity:
            product.inventory -= quantity
            await self.update(product)
        return product
