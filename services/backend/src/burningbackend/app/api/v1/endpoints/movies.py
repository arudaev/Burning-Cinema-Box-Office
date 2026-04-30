from fastapi import APIRouter, Depends, HTTPException

from burningbackend.app.core.deps import get_current_user, get_current_superuser
from burningbackend.app.models.movie import Movie, UpdateMovie
from burningbackend.app.models.user import User

router = APIRouter()


@router.post("/", response_description="Movie added to the database")
async def add_movie(movie: Movie, _: User = Depends(get_current_user)) -> dict:
    await movie.create()
    movie = await Movie.find_one({"name": movie.name})
    return {"message": "Movie added successfully", "data": movie}


@router.get("/", response_description="Movies retrieved")
async def get_movies() -> list[Movie]:
    return await Movie.find({"active": True}).to_list()


@router.get("/name/{name}", response_description="Movie retrieved")
async def get_movie_by_name(name: str) -> Movie:
    movie = await Movie.find_one({"name": name})
    if movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie


@router.get("/{id}", response_description="Movie retrieved")
async def get_movie(id: str) -> Movie:
    movie = await Movie.get(id)
    if movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie


@router.put("/{id}", response_description="Movie data updated")
async def update_movie(id: str, req: UpdateMovie, _: User = Depends(get_current_user)) -> dict:
    movie = await Movie.get(id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie record not found")
    update_data = {k: v for k, v in req.dict().items() if v is not None}
    updated_movie = await movie.update({"$set": update_data})
    return {"message": "Movie updated successfully", "data": updated_movie}


@router.delete("/{id}", response_description="Movie deactivated")
async def delete_movie(id: str, _: User = Depends(get_current_superuser)) -> dict:
    movie = await Movie.get(id)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie record not found")
    await movie.update({"$set": {"active": False}})
    movie = await Movie.get(id)
    return {"message": "Movie deactivated successfully", "data": movie}
