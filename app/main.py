from typing import Optional

from fastapi import FastAPI
import requests
from app.services import MovieService

app = FastAPI()


@app.get("/")
def health_check():
    return {"Hello": "World"}


@app.get("/movies")
def list_movies(
    genre: Optional[str] = None,  # TODO: decode value
    offset: Optional[int] = None,
    limit: Optional[int] = None,
):
    service = MovieService(requests)
    if genre:
        genre = service.get_genre(genre)

    return service.list(genre, offset=offset, limit=limit)
