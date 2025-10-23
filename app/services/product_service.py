"""Product service for business logic."""
from app.db.models.product import Product
from fastapi import HTTPException


class ProductService:
    """
    Service layer for product operations.
    Handles product retrieval, search, and filtering.
    """

    @staticmethod
    async def list_products(search_query: str | None = None, skip: int = 0, limit: int = 20) -> list[Product]:
        """
        Get list of products with optional search and pagination.
        
        Args:
            search_query: Optional search term for name or category
            skip: Number of items to skip
            limit: Maximum number of items to return
            
        Returns:
            List of products matching criteria
        """
        query = {}
        if search_query:
            query = {
                "$or": [
                    {"name": {"$regex": search_query, "$options": "i"}},
                    {"category": {"$regex": search_query, "$options": "i"}}
                ]
            }
        return await Product.find(query).skip(skip).limit(limit).to_list()

    @staticmethod
    async def get_product_by_slug(slug: str) -> Product:
        """
        Get a single product by its slug.
        
        Args:
            slug: Product slug identifier
            
        Returns:
            Product if found and active
            
        Raises:
            HTTPException: If product not found or inactive
        """
        product = await Product.find_one(Product.slug == slug, Product.is_active == True)
        if not product:
            raise HTTPException(404, "Product not found")
        return product

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
        return product

