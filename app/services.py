from typing import List, Optional
from typing_extensions import TypedDict
import requests
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse, unquote
from app.entities import Genre
from app.entities import GENRES_MAP
from structlog import get_logger
from app.entities import Error
from datetime import date
from app.schemas import Cast, Movie
import json

logger = get_logger()


class MovieService:
    class MovieDetailsResponse(TypedDict):
        id: str
        title: str
        releaseDate: str
        revenue: str
        posterPath: str
        genres: List[int]
        cast: List[int]

    def __init__(self, client: requests) -> None:
        self.client = client
        self.errors: List[Error] = None

    def add_error(self, error: Error) -> None:
        if self.errors is None:
            self.errors = [error]
        else:
            self.errors.append(error)

    def list(self, genre: Genre, offset: int, limit: int) -> List[Movie]:
        """Given a genre list movies"""
        movies_ids = self.list_ids(genre, offset=offset, limit=limit)
        movies = self.get_details(movies_ids)

        return movies

    def list_ids(
        self,
        genre: Optional[Genre] = None,  # TODO: confirm
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> List[int]:
        url = "http://localhost:3040/movies"
        query_params = {}

        if genre:
            query_params["genre"] = genre["name"]

        if offset is not None:
            query_params["offset"] = offset

        if limit is not None:
            query_params["limit"] = limit

        if query_params:
            url = self.add_query_params_to_url(url, query_params)

        logger.info("GET movies ids", url=unquote(url))
        response = self.request_until_status_code_is_200(self.client, url)

        return response.json()["data"]

    @staticmethod
    def request_until_status_code_is_200(client, url) -> dict:
        status_code = None
        while status_code != 200:
            response = client.get(url)
            if (status_code := response.status_code) == 200:
                break

            logger.error(
                "Response Error",
                status_code=status_code,
                url=url,
                response=response.text,
            )

        logger.info(
            "Response Sucessfull",
            url=unquote(url),
            status_code=status_code,
            response=response.json(),
        )
        return response

    @staticmethod
    def build_id_query_params(values: List[int]) -> dict:
        """Build query params for id in singular or multiples ids

        Given values with:
            * one id: return {'id': ...}
            * multiples ids: return {'ids': ...}
        """

        if len(values) == 1:
            return {"id": str(values[0])}

        return {"ids": ",".join([str(m) for m in values])}

    @staticmethod
    def build_details_url(movies_ids: List[int]) -> str:  # TYPING: str[URL]
        url = "http://localhost:3030/movies"
        query_params = MovieService.build_id_query_params(movies_ids)

        return MovieService.add_query_params_to_url(url, query_params)

    def handle_details_request(
        self, movies_ids: List[int]
    ) -> List[MovieDetailsResponse]:
        url = self.build_details_url(movies_ids)
        logger.info("GET movies details", url=unquote(url))
        response = self.client.get(url)

        response = self.request_until_status_code_is_200(self.client, url)

        return [
            self.MovieDetailsResponse(
                id=movie_res["id"],
                title=movie_res["title"],
                releaseDate=movie_res["releaseDate"],
                revenue=movie_res["revenue"],
                posterPath=movie_res["posterPath"],
                genres=movie_res["genres"],
                cast=movie_res["cast"],
            )
            for movie_res in response.json()["data"]
        ]

    def build_movie_details_from_response(
        self, response: MovieDetailsResponse
    ) -> List[Movie]:
        movies_details: List[Movie] = []
        for res in response:
            mid = res["id"]

            cast = None
            if cast_ids := res.get("cast"):
                cast = self.get_cast(cast_ids)

            if not cast:
                self.add_error(
                    Error(
                        errorCode=440,
                        message=f"Movie id #{mid} cast info is not complete",
                    )
                )

            movie = Movie(
                id=mid,
                title=res["title"],
                releaseYear=date.fromisoformat(res["releaseDate"]).year,
                revenue="US$ {:,.0f}".format(res["revenue"]),
                posterPath=res["posterPath"],
                genres=self.get_genres_names_from_list(res["genres"]),
                cast=cast,
            )
            movies_details.append(movie)

        return movies_details

    def get_details(self, movies_ids: List[int]) -> List[Movie]:
        """Given a list of movies id's returns a list with movies details"""
        # FIXME: can not send more than 5 movides_ids

        movies_list: list = []

        while movies_ids:
            movies_batch = movies_ids[:5]

            if response := self.handle_details_request(movies_batch):
                movies_detail_batch = self.build_movie_details_from_response(response)
                movies_list += movies_detail_batch

            for _ in range(5):
                if not movies_ids:
                    break
                movies_ids.pop(0)

        return movies_list

    def get_cast(self, cast_list: List[int]) -> Optional[List[Cast]]:
        # TODO
        return

    @staticmethod
    def add_query_params_to_url(url: str, query_params: dict) -> str:
        """Add query_params dict to the url"""
        url_parts = list(urlparse(url))
        query = dict(parse_qsl(url_parts[4]))
        query.update(query_params)
        url_parts[4] = urlencode(query)

        return urlunparse(url_parts)

    @staticmethod
    def get_genres_names_from_list(genres: List[int]) -> Optional[List[Genre]]:
        return [
            MovieService.get_genre(g).name for g in genres if MovieService.get_genre(g)
        ]

    @staticmethod
    def get_genre(name: str) -> Optional[Genre]:
        for genre in GENRES_MAP:
            if name == genre["name"]:
                return Genre(id=genre["id"], name=genre["name"])
