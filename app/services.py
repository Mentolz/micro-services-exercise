from typing import List, Optional
import requests
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse
from app.entities import Genre
from app.entities import GENRES_MAP
from structlog import get_logger

logger = get_logger()

def add_query_params_to_url(url: str, query_params: dict) -> str:
    """Add query_params dict to the url"""
    url_parts = list(urlparse(url))
    query = dict(parse_qsl(url_parts[4]))
    query.update(query_params)
    url_parts[4] = urlencode(query)

    return urlunparse(url_parts)


def get_genre(name: str) -> Optional[Genre]:
    for genre in GENRES_MAP:
        if name == genre["name"]:
            return Genre(id=genre["id"], name=genre["name"])


def list_movies_ids(
    genre: Optional[Genre], offset: Optional[int], limit: Optional[int]
) -> List[int]:
    url = "http://localhost:3040/movies"

    query_params = {}
    if genre:
        query_params["genre"] = genre["name"]

    if offset:
        query_params["offset"] = offset

    if limit:
        query_params["limit"] = limit

    if query_params:
        url = add_query_params_to_url(url, query_params)

    logger.info("GET", url=url)
    response = requests.get(url)
    # TODO: handle with != 200 ok

    if response.status_code != 200:
        logger.error("Response Error", status_code=response.status_code)

    return response.json()["data"]
