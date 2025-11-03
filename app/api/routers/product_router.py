from fastapi import APIRouter, Query, Path, Request, Depends
from app.api.service_deps import get_product_service
from app.services.product_service import ProductService
from app.api.rate_limit import limiter, PRODUCT_RATE_LIMIT

router = APIRouter()

@router.get("")
@limiter.limit(PRODUCT_RATE_LIMIT)
async def list_products(
    request: Request,
    product_service: ProductService = Depends(get_product_service),
    q: str | None = Query(None, example="laptop", description="Search query for product name or category"),
    skip: int = Query(0, ge=0, example=0, description="Number of items to skip"),
    limit: int = Query(20, ge=1, le=100, example=20, description="Maximum number of items to return")
):
    """
    Get list of products with optional search and pagination.

    Returns a list of products matching the search criteria.

    **Rate Limit:** 5 requests per minute per IP address.
    """
    return await product_service.list_products(q, skip, limit)

@router.get("/{slug}")
@limiter.limit(PRODUCT_RATE_LIMIT)
async def get_by_slug(request: Request, slug: str = Path(..., example="gaming-laptop-pro", description="Product slug identifier"), product_service: ProductService = Depends(get_product_service)):
    """
    Get a single product by its slug.

    Returns product details if found and active.

    **Rate Limit:** 5 requests per minute per IP address.
    """
    return await product_service.get_product_by_slug(slug)
