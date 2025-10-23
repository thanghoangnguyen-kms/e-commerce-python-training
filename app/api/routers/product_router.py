from fastapi import APIRouter, Query, Path
from app.services.product_service import ProductService

router = APIRouter()

@router.get("")
async def list_products(
    q: str | None = Query(None, example="laptop", description="Search query for product name or category"),
    skip: int = Query(0, ge=0, example=0, description="Number of items to skip"),
    limit: int = Query(20, ge=1, le=100, example=20, description="Maximum number of items to return")
):
    """
    Get list of products with optional search and pagination.

    Returns a list of products matching the search criteria.
    """
    return await ProductService.list_products(q, skip, limit)

@router.get("/{slug}")
async def get_by_slug(slug: str = Path(..., example="gaming-laptop-pro", description="Product slug identifier")):
    """
    Get a single product by its slug.

    Returns product details if found and active.
    """
    return await ProductService.get_product_by_slug(slug)
