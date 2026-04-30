from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4

from beanie import Document
from beanie import PydanticObjectId
from pydantic import BaseModel, Field

from burningbackend.app.models.inventory import Category


class VatLine(BaseModel):
    rate: float
    net: float
    vat: float
    gross: float


class Product(BaseModel):
    name: str
    amount: int
    price: float
    category: Category
    is_deposit: bool = False
    vat_rate: float = 0.0


class History(Document):
    timestamp: datetime
    total: float
    isteam: bool
    movie: str
    cancellation: bool = False
    products: List[Product]
    transaction_id: UUID = Field(default_factory=uuid4)
    staff_id: Optional[PydanticObjectId] = None
    vat_breakdown: List[VatLine] = Field(default_factory=list)

    class Settings:
        name = "history"
