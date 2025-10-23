from beanie import Document, Indexed
from pydantic import BaseModel
from datetime import datetime

class OrderItem(BaseModel):
    product_id: str
    name: str
    unit_price: float
    qty: int
    line_total: float

class Order(Document):
    user_id: Indexed(str)  # type: ignore
    items: list[OrderItem]
    total: float
    currency: str = "usd"
    status: str = "pending"  # pending|paid|canceled|failed
    created_at: datetime = datetime.utcnow()

    class Settings:
        name = "orders"
