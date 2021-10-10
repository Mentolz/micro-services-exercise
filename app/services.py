from typing import Iterable, List, Optional
from typing_extensions import TypedDict
import requests
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse, unquote
from app.entities import Genre
from app.entities import GENRES_MAP
from structlog import get_logger
from app.entities import Error
from datetime import date
from app.schemas import CastMember, Movie

logger = get_logger()


class BaseService:
    def __init__(self, client: requests) -> None:
        self.client = client
        self.errors: Optional[List[Error]] = None

    def _add_error(self, error: Error) -> None:
        if self.errors is None:
            self.errors = [error]
        else:
            self.errors.append(error)

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
    def get_details_url(ids: List[int], url) -> str:  # TYPING: str[URL]
        query_params = BaseService.build_id_query_params(ids)

        return BaseService.add_query_params_to_url(url, query_params)

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
    def add_query_params_to_url(url: str, query_params: dict) -> str:
        """Add query_params dict to the url"""
        url_parts = list(urlparse(url))
        query = dict(parse_qsl(url_parts[4]))
        query.update(query_params)
        url_parts[4] = urlencode(query)

        return urlunparse(url_parts)

    @staticmethod
    def split_list_with_max_length(list_, max_length) -> List[List[int]]:
        new_list: list = []

        while list_:
            new_list.append(list_[:max_length])
            for _ in range(max_length):
                if not list_:
                    break
                list_.pop(0)

        return new_list

    @staticmethod
    def filter(
        values: Iterable, offset: Optional[int], limit: Optional[int]
    ) -> Iterable:
        if offset:
            values = values[offset:]

        if limit:
            values = values[:limit]

        return values


class MovieService(BaseService):
    class MovieDetailsResponse(TypedDict):
        id: str
        title: str
        releaseDate: str
        revenue: str
        posterPath: str
        genres: List[int]
        cast: List[int]

    def list(
        self, genre: Optional[Genre], offset: Optional[int], limit: Optional[int]
    ) -> tuple[List[Movie], int]:
        """Given a genre list movies"""
        movies_ids = self.list_ids(genre)
        total = len(movies_ids)
        movies_ids = self.filter(movies_ids, offset, limit)
        movies = self.get_details(movies_ids)

        return movies, total

    def list_ids(self, genre: Optional[Genre] = None) -> List[int]:
        url = "http://localhost:3040/movies"
        query_params = {}

        if genre:
            query_params["genre"] = genre["name"]

        if query_params:
            url = self.add_query_params_to_url(url, query_params)

        logger.info("GET movies ids", url=unquote(url))
        response = self.request_until_status_code_is_200(self.client, url)

        return response.json()["data"]

    def get_details(self, movies_ids: List[int]) -> List[Movie]:
        """Given a list of movies id's returns a list with movies details"""
        movies_list: list = []

        for movies_batch in self.split_list_with_max_length(movies_ids, 5):
            details = self._request_details(movies_batch)
            if details:
                movies_detail_batch = self._build_details_from_response(details)
                movies_list += movies_detail_batch

        return movies_list

    def _request_details(self, movies_ids: List[int]) -> List[MovieDetailsResponse]:
        url = self.get_details_url(movies_ids, "http://localhost:3030/movies")
        logger.info("GET movies details", url=unquote(url))
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

    def _build_details_from_response(
        self, response: MovieDetailsResponse
    ) -> List[Movie]:
        movies_details: List[Movie] = []
        for res in response:
            mid = res["id"]

            cast = None
            if cast_ids := res.get("cast"):
                cast_service = CastService(self.client)
                cast = cast_service.get_details(cast_ids)

            if not cast or cast_service.errors:
                message = f"Movie id #{mid} cast info is not complete"
                self._add_error(
                    Error(
                        errorCode=440,
                        message=message,
                    )
                )
                logger.warning(message, id=mid, cast_ids=cast_ids)

            movie = Movie(
                id=mid,
                title=res["title"],
                releaseYear=date.fromisoformat(res["releaseDate"]).year,
                revenue="US$ {:,.0f}".format(res["revenue"]),
                posterPath=res["posterPath"],
                genres=get_genres_names_from_list(res["genres"]),
                cast=cast,
            )
            movies_details.append(movie)

        return movies_details


class CastService(BaseService):
    def get_details(self, cast_ids: List[int]) -> Optional[List[CastMember]]:
        cast: list = []
        for cast_batch_ids in self.split_list_with_max_length(cast_ids, 5):
            url = self.get_details_url(cast_batch_ids, "http://localhost:3050/artists")
            response = self.client.get(url)

            if response.status_code == 200:
                cast += [
                    CastMember(
                        id=member["id"],
                        gender=member["gender"],
                        name=member["name"],
                        profilePath=member["profilePath"],
                    )
                    for member in response.json()["data"]
                ]
            else:
                logger.warning(
                    "Cast details request failed",
                    url=unquote(url),
                    status_code=response.status_code,
                    response=response.text,
                )
                self._add_error(
                    Error(
                        errorCode=460,
                        message=f"Cast id's #{cast_batch_ids} details info is not complete",
                    )
                )

        return cast or None


def get_genre(name: str) -> Optional[Genre]:
    for genre in GENRES_MAP:
        if name == genre["name"]:
            return Genre(id=genre["id"], name=genre["name"])


def get_genres_names_from_list(ids_list: List[int]) -> Optional[List[Genre.__name__]]:
    return [genre["name"] for genre in GENRES_MAP if genre["id"] in ids_list]
