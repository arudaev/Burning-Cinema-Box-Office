from typing import Optional
from enum import Enum

from beanie import Document, Indexed
from pydantic import BaseModel


class Category(str, Enum):
    DRINKS = 'Drinks'
    SNACKS = 'Snacks'
    SWEETS = 'Sweets'
    TICKETS = 'Tickets'
    PFAND = 'Pfand'


class Inventory(Document):
    name: Indexed(str, unique=True)
    amount: int = 0
    price: float
    price_team: float
    amount_sold: int = 0
    category: Category = Category.DRINKS
    vat_rate: float
    is_deposit: bool = False
    requires_deposit: bool = False
    active: bool = True

    class Settings:
        name = "inventory"


class UpdateInventory(BaseModel):
    name: Optional[str] = None
    amount: Optional[int] = None
    price: Optional[float] = None
    price_team: Optional[float] = None
    amount_sold: Optional[int] = None
    category: Optional[Category] = None
    vat_rate: Optional[float] = None
    is_deposit: Optional[bool] = None
    requires_deposit: Optional[bool] = None
    active: Optional[bool] = None
