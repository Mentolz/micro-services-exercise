from typing import Optional, TypedDict, List
from app import schemas
from fastapi import FastAPI
import requests
from app.services import MovieService
from app.entities import Error
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
    offset: Optional[int] = 0,  # TODO: review this
    limit: Optional[int] = None,
):
    movie_service = MovieService(requests)
    if genre:
        genre = movie_service.get_genre(unquote_plus(genre))

    movies: List[schemas.Movie] = movie_service.list(genre, offset=offset, limit=limit)
    errors: List[Error] = movie_service.errors

    return MoviesOutput(
        data=DataMovies(movies=movies),
        metadata=MetaData(offset=offset, limit=limit, total=0),  # FIXME
        errors=errors,
    )
