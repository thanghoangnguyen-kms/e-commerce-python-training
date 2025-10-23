from beanie import Document, Indexed
from pydantic import Field
from datetime import datetime

class Product(Document):
    product_id: Indexed(int, unique=True)  # type: ignore
    name: Indexed(str)  # type: ignore
    slug: Indexed(str, unique=True)  # type: ignore
    description: str | None = None
    price: float = Field(..., gt=0, description="Product price in USD")
    image: str | None = Field(None, description="Product image URL")
    inventory: int = 0
    category: str | None = None
    is_active: bool = True
    created_at: datetime = datetime.utcnow()

    class Settings:
        name = "products"
