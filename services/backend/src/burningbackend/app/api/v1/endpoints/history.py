from bson.objectid import ObjectId

from fastapi import APIRouter, Depends, HTTPException

from burningbackend.app.core.deps import get_current_user
from burningbackend.app.models.history import History
from burningbackend.app.models.user import User

router = APIRouter()


@router.get("/", response_description="History retrieved")
async def get_history(movie: str = None, cancellation: bool = False) -> list[History]:
    query: dict = {"cancellation": cancellation}
    if movie is not None:
        query["movie"] = movie
    return await History.find(query).to_list()


@router.post("/", response_description="History item added to the database")
async def add_history(history: History, _: User = Depends(get_current_user)) -> dict:
    await history.create()
    history = await History.find_one({"timestamp": history.timestamp})
    return {"message": "History added successfully", "data": history}


@router.post("/cancel/", response_description="Order cancelled")
async def cancel_history(_id: str, cancellation: bool = True, _: User = Depends(get_current_user)) -> dict:
    history = await History.get(ObjectId(_id))
    if not history:
        raise HTTPException(status_code=404, detail="History record not found")
    history.cancellation = cancellation
    await history.save()
    return {"message": "History updated successfully", "data": history}


@router.get("/total", response_description="Total revenue for a movie")
async def get_total(movie: str, isteam: bool = False, cancellation: bool = False, pfand: bool = True) -> float:
    query: dict = {"movie": movie, "cancellation": cancellation}
    if isteam:
        query["isteam"] = True
    history = await History.find(query).to_list()
    total = sum(h.total for h in history)
    if not pfand:
        for h in history:
            for p in h.products:
                if p.is_deposit:
                    total -= p.price * p.amount
    return float(total)


@router.get("/tickets", response_description="Ticket count for a movie")
async def get_tickets(movie: str, isteam: bool = False, freeticket: bool = False) -> int:
    query: dict = {"movie": movie, "cancellation": False, "isteam": isteam}
    history = await History.find(query).to_list()
    total = 0
    for h in history:
        for p in h.products:
            if p.name == "Ticket":
                total += p.amount
            if freeticket and p.name == "Freiticket":
                total += p.amount
    return total
