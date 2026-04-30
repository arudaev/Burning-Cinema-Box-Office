from datetime import datetime
from typing import Optional

from beanie import Document
from pydantic import BaseModel


class Reservation(Document):
    timestamp: datetime
    movie: str
    seat_number: int
    email: str
    scanned: bool = False
    retention_until: datetime
    scan_timestamp: Optional[datetime] = None

    class Settings:
        name = "reservations"


class ScanReservation(BaseModel):
    scanned: bool = True
