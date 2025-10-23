from beanie import Document, Indexed
from pydantic import BaseModel
from datetime import datetime

class CartItem(BaseModel):
    product_id: str
    qty: int

class Cart(Document):
    user_id: Indexed(str)  # type: ignore
    items: list[CartItem] = []
    updated_at: datetime = datetime.utcnow()

    class Settings:
        name = "carts"
