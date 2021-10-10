from typing import Optional, TypedDict, List
from app import schemas
from fastapi import FastAPI
import requests
from app.entities import Error
from app.services import MovieService, get_genre
from urllib.parse import unquote_plus

app = FastAPI()


@app.get("/")
def health_check():
    return {"Hello": "World"}


class DataMovies(TypedDict):
    movies: List[schemas.Movie]


class MetaData(TypedDict):
    offset: int
    limit: Optional[int]
    total: int  # TODO


class MoviesOutput(TypedDict):
    data: DataMovies
    metadata: MetaData
    errors: Optional[List[Error]]


@app.get("/movies", response_model=MoviesOutput)
def list_movies(
    genre: Optional[str] = None,
    offset: Optional[int] = 0,
    limit: Optional[int] = 10,
):
    movie_service = MovieService(requests)
    if genre:
        genre = get_genre(unquote_plus(genre))

    movies, total = movie_service.list(genre, offset, limit)
    errors = movie_service.errors

    return MoviesOutput(
        data=DataMovies(movies=movies),
        metadata=MetaData(
            offset=offset,
            limit=limit if total >= limit else total,
            total=total
        ),
        errors=errors,
    )
