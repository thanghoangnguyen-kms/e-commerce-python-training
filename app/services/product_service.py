"""Product service for business logic only."""
import logging
from app.db.models.product import Product
from app.core.cache_decorator import cached, invalidate_cache
from fastapi import HTTPException

logger = logging.getLogger(__name__)


class ProductService:
    """
    Service layer for product operations.
    Contains only business logic - all caching and performance monitoring
    is handled by the @cached decorator in cache_decorator.py
    """

    @staticmethod
    @cached(
        namespace="products",
        key_builder=lambda search_query=None, skip=0, limit=20: f"list:q={search_query or 'all'}:skip={skip}:limit={limit}"
    )
    async def list_products(search_query: str | None = None, skip: int = 0, limit: int = 20) -> list[dict]:
        """
        Get list of products with optional search and pagination.

        Args:
            search_query: Optional search term for name or category
            skip: Number of items to skip
            limit: Maximum number of items to return

        Returns:
            List of products matching criteria (as dictionaries for JSON serialization)
        """
        query = {}
        if search_query:
            query = {
                "$or": [
                    {"name": {"$regex": search_query, "$options": "i"}},
                    {"category": {"$regex": search_query, "$options": "i"}}
                ]
            }

        products = await Product.find(query).skip(skip).limit(limit).to_list()
        return [product.model_dump() for product in products] if products else []

    @staticmethod
    @cached(
        namespace="products",
        key_builder=lambda slug: f"slug:{slug}"
    )
    async def get_product_by_slug(slug: str) -> dict:
        """
        Get a single product by its slug.

        Args:
            slug: Product slug identifier

        Returns:
            Product if found and active (as dictionary for JSON serialization)

        Raises:
            HTTPException: If product not found or inactive
        """
        product = await Product.find_one(Product.slug == slug, Product.is_active == True)
        if not product:
            raise HTTPException(404, "Product not found")

        return product.model_dump()

    @staticmethod
    async def get_product_by_id(product_id: str) -> Product:
        """
        Get a product by its MongoDB ID.

        Args:
            product_id: MongoDB document ID

        Returns:
            Product if found

        Raises:
            HTTPException: If product not found
        """
        product = await Product.get(product_id)
        if not product:
            raise HTTPException(404, "Product not found")
        return product

    @staticmethod
    async def create_product(
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
        """
        Create a new product.

        Raises:
            HTTPException: If slug or product_id already exists
        """
        if await Product.find_one(Product.slug == slug):
            raise HTTPException(400, "Slug already exists")
        if await Product.find_one(Product.product_id == product_id):
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
        await product.insert()

        # Invalidate all product list caches (since a new product was added)
        await invalidate_cache("products", "list:*")

        return product

    @staticmethod
    async def update_product(
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
        Update an existing product.

        Args:
            product_id: MongoDB document ID of product to update

        Raises:
            HTTPException: If product not found or new product_id already exists
        """
        product = await Product.get(product_id)
        if not product:
            raise HTTPException(404, "Product not found")

        # Check if product_id is being changed and if new ID already exists
        if product.product_id != new_product_id:
            existing = await Product.find_one(Product.product_id == new_product_id)
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
        await product.save()

        # Invalidate caches: specific product cache and all list caches
        await invalidate_cache("products", f"slug:{old_slug}")
        if old_slug != slug:  # If slug changed, also delete new slug cache
            await invalidate_cache("products", f"slug:{slug}")
        await invalidate_cache("products", "list:*")

        return product

