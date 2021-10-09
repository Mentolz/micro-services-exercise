from typing import List, Optional
import requests
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse
from app.entities import Genre
from app.entities import GENRES_MAP
from structlog import get_logger

logger = get_logger()


class MovieService:
    def __init__(self, client: requests) -> None:
        self.client = client

    def list(self, genre: Genre, offset: int, limit: int) -> dict:
        """Given a genre list movies"""
        movies_ids = self.list_ids(genre, offset=offset, limit=limit)

        return self.get_details(movies_ids)

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

        logger.info("GET", url=url)

        status_code = None
        while status_code != 200:
            response = self.client.get(url)
            status_code = response.status_code
            if status_code != 200:
                logger.error("Response Error", status_code=status_code, url=url)

        logger.info("Response Sucessfull", status_code=status_code, url=url)

        return response.json()["data"]

    def get_details(self, movies: List[int]):
        """Given a list of movies id's returns a list with movies details"""
        url = "http://localhost:3030/movies"

        if len(movies) == 1:
            query_params = {"id": str(movies[0])}
        else:
            # TODO: cant be larger can 5
            query_params = {"ids": ",".join([str(m) for m in movies])}

        url = self.add_query_params_to_url(url, query_params)

        logger.info("GET", url=url)

        response = self.client.get(url)

        if response.status_code != 200:
            logger.warning(
                "Response Error, returning movies details with missing detail info",
                status_code=response.status_code,
                url=url,
            )
            return  # TODO: send event code info

        logger.info("Response Sucessfull", status_code=response.status_code, url=url)

        return response.json()["data"]

    @staticmethod
    def add_query_params_to_url(url: str, query_params: dict) -> str:
        """Add query_params dict to the url"""
        url_parts = list(urlparse(url))
        query = dict(parse_qsl(url_parts[4]))
        query.update(query_params)
        url_parts[4] = urlencode(query)

        return urlunparse(url_parts)

    @staticmethod
    def get_genre(name: str) -> Optional[Genre]:
        for genre in GENRES_MAP:
            if name == genre["name"]:
                return Genre(id=genre["id"], name=genre["name"])
