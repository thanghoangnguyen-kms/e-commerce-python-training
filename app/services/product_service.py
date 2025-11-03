"""Product service for business logic only."""
from app.db.models.product import Product
from app.repositories.product_repository import ProductRepository
from app.core.cache_decorator import cached, invalidate_cache
from app.core.service_decorator import service_method
from fastapi import HTTPException


class ProductService:
    """
    Service layer for product operations.
    Contains only business logic - all caching and performance monitoring
    is handled by the @cached decorator in cache_decorator.py
    """

    def __init__(self, product_repository: ProductRepository = None):
        """Initialize ProductService with repository dependency."""
        self.product_repository = product_repository or ProductRepository()

    @service_method
    @cached(
        namespace="products",
        key_builder=lambda self, search_query=None, skip=0, limit=20: f"list:q={search_query or 'all'}:skip={skip}:limit={limit}"
    )
    async def list_products(self, search_query: str | None = None, skip: int = 0, limit: int = 20) -> list[Product]:
        """
        Get list of products with optional search and pagination.
        Returns products as Product model objects with MongoDB id field included.
        """
        products = await self.product_repository.search_products(search_query, skip, limit)
        return products if products else []

    @service_method
    @cached(
        namespace="products",
        key_builder=lambda self, slug: f"slug:{slug}"
    )
    async def get_product_by_slug(self, slug: str) -> Product:
        """
        Get a single product by its slug.
        Returns product as Product model object with MongoDB id field included.
        """
        product = await self.product_repository.find_by_slug(slug, active_only=True)
        if not product:
            raise HTTPException(404, "Product not found")

        return product

    @service_method
    async def get_product_by_id(self, product_id: str) -> Product:
        """
        Get a product by its MongoDB ObjectId.
        Returns product as Product model object.
        """
        product = await self.product_repository.get_by_id(product_id)
        if not product:
            raise HTTPException(404, "Product not found")
        return product

    @service_method
    async def create_product(
        self,
        product_id: int,
        name: str,
        slug: str,
        description: str | None,
        price: float,
        image: str | None,
        inventory: int,
        category: str | None,
        is_active: bool
    ) -> Product:
        """Create a new product. Returns Product model object with MongoDB id."""
        if await self.product_repository.find_by_slug(slug, active_only=False):
            raise HTTPException(400, "Slug already exists")
        if await self.product_repository.find_by_product_id(product_id):
            raise HTTPException(400, "Product ID already exists")

        product = Product(
            product_id=product_id,
            name=name,
            slug=slug,
            description=description,
            price=price,
            image=image,
            inventory=inventory,
            category=category,
            is_active=is_active,
        )
        await self.product_repository.create(product)

        # Invalidate all product list caches (since a new product was added)
        await invalidate_cache("products", "list:*")

        return product

    @service_method
    async def update_product(
        self,
        product_id: str,
        new_product_id: int,
        name: str,
        slug: str,
        description: str | None,
        price: float,
        image: str | None,
        inventory: int,
        category: str | None,
        is_active: bool
    ) -> Product:
        """
        Update an existing product by MongoDB ObjectId.
        Returns updated Product model object with MongoDB id.
        """
        product = await self.product_repository.get_by_id(product_id)
        if not product:
            raise HTTPException(404, "Product not found")

        # Check if product_id is being changed and if new ID already exists
        if product.product_id != new_product_id:
            existing = await self.product_repository.find_by_product_id(new_product_id)
            if existing:
                raise HTTPException(400, "Product ID already exists")

        old_slug = product.slug

        product.product_id = new_product_id
        product.name = name
        product.slug = slug
        product.description = description
        product.price = price
        product.image = image
        product.inventory = inventory
        product.category = category
        product.is_active = is_active
        await self.product_repository.update(product)

        # Invalidate caches: specific product cache and all list caches
        await invalidate_cache("products", f"slug:{old_slug}")
        if old_slug != slug:  # If slug changed, also delete new slug cache
            await invalidate_cache("products", f"slug:{slug}")
        await invalidate_cache("products", "list:*")

        return product

    @service_method
    async def delete_product(self, product_id: str) -> dict:
        """
        Delete a product by its MongoDB ObjectId.
        Returns confirmation with deleted product details.
        """
        product = await self.product_repository.get_by_id(product_id)
        if not product:
            raise HTTPException(404, "Product not found")

        # Store slug for cache invalidation
        product_slug = product.slug

        # Delete the product
        await self.product_repository.delete(product)

        # Invalidate caches: specific product cache and all list caches
        await invalidate_cache("products", f"slug:{product_slug}")
        await invalidate_cache("products", "list:*")

        return {
            "message": "Product deleted successfully",
            "product_id": product_id,
            "slug": product_slug,
            "name": product.name
        }
