from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException

from burningbackend.app.core.deps import get_current_user
from burningbackend.app.models.movie import Movie
from burningbackend.app.models.reservation import Reservation
from burningbackend.app.models.user import User

router = APIRouter()


@router.get("/reservations", response_description="Reservations retrieved")
async def get_all_reservations() -> list[Reservation]:
    reservations = await Reservation.all().to_list()
    if not reservations:
        raise HTTPException(status_code=404, detail="No reservations found")
    return reservations


@router.post("/reservation/add", response_description="Reservation added to the database")
async def add_reservation(reservation: Reservation, _: User = Depends(get_current_user)) -> dict:
    movie = await Movie.find_one({"name": reservation.movie})
    if not movie:
        raise HTTPException(status_code=404, detail=f"Movie '{reservation.movie}' not found")
    reservation.retention_until = movie.datetime + timedelta(days=30)
    await reservation.create()
    reservation = await Reservation.find_one({"timestamp": reservation.timestamp})
    return {"message": "Reservation added successfully", "data": reservation}


@router.put("/reservation/update/{id}", response_description="Reservation updated in the database")
async def update_reservation(id: str, reservation: Reservation, _: User = Depends(get_current_user)) -> dict:
    existing = await Reservation.get(id)
    if not existing:
        raise HTTPException(status_code=404, detail="Reservation record not found")
    update_data = {k: v for k, v in reservation.dict().items() if v is not None}
    updated = await existing.update({"$set": update_data})
    return {"message": "Reservation updated successfully", "data": updated}


@router.post("/reservation/scan/{id}", response_description="Reservation scanned")
async def scan_reservation(id: str, _: User = Depends(get_current_user)) -> dict:
    reservation = await Reservation.get(id)
    if not reservation:
        raise HTTPException(status_code=404, detail="Reservation record not found")
    if reservation.scanned:
        raise HTTPException(status_code=400, detail="Reservation already scanned")
    await reservation.update({"$set": {"scanned": True, "scan_timestamp": datetime.utcnow()}})
    reservation = await Reservation.get(id)
    return {"message": "Reservation scanned successfully", "data": reservation}
