from fastapi import APIRouter

from burningbackend.app.api.v1.endpoints import movies, inventory, history, reservation, report, auth
from burningbackend.app.core.config import settings

router = APIRouter(prefix=f"/{settings.API_V1_STR}")


@router.get("/health", tags=["Health"])
async def health() -> dict:
    return {"status": "ok"}


router.include_router(auth.router, prefix="/auth", tags=["Auth"])
router.include_router(movies.router, prefix="/movies", tags=["Movies"])
router.include_router(inventory.router, prefix="/inventory", tags=["Inventory"])
router.include_router(history.router, prefix="/history", tags=["History"])
router.include_router(reservation.router, prefix="/reservation", tags=["Reservation"])
router.include_router(report.router, prefix="/report", tags=["Report"])
