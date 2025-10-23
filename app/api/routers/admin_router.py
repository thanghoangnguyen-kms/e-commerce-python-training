from fastapi import APIRouter, Depends, Path
from app.api.deps import admin_required
from app.services.product_service import ProductService
from app.schemas.product import ProductCreateRequest, ProductUpdateRequest

router = APIRouter()

@router.post("/products")
async def create_product(data: ProductCreateRequest, _=Depends(admin_required)):
    """
    Create a new product (Admin only).

    Creates a new product in the catalog with the provided details.
    """
    return await ProductService.create_product(
        product_id=data.product_id,
        name=data.name,
        slug=data.slug,
        description=data.description,
        price=data.price,
        image=data.image,
        inventory=data.inventory,
        category=data.category,
        is_active=data.is_active
    )

@router.patch("/products/{product_id}")
async def update_product(
    product_id: str = Path(..., example="67123abc456def789012345", description="MongoDB document ID"),
    data: ProductUpdateRequest = ...,
    _=Depends(admin_required)
):
    """
    Update an existing product (Admin only).

    Updates all fields of the specified product.
    """
    return await ProductService.update_product(
        product_id=product_id,
        new_product_id=data.product_id,
        name=data.name,
        slug=data.slug,
        description=data.description,
        price=data.price,
        image=data.image,
        inventory=data.inventory,
        category=data.category,
        is_active=data.is_active
    )
