from typing import Optional

from fastapi import FastAPI
from app import services

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
    if genre:
        genre = services.get_genre(genre)

    return services.list_movies_ids(genre, offset=offset, limit=limit)
