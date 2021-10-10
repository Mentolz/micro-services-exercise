from app.services import InterfaceService, MovieService, get_genre
import pytest
from typing import Optional, List


@pytest.mark.parametrize(
    "url,query_params,expected_url",
    (
        (
            "http://localhost:3040/movies",
            {"offset": 0, "limit": 10},
            "http://localhost:3040/movies?offset=0&limit=10",
        ),
        (
            "http://localhost:3040/movies",
            {"offset": None, "limit": 10},
            "http://localhost:3040/movies?offset=None&limit=10",
        ),
        (
            "http://localhost:3040/movies?offset=0",
            {"limit": 10},
            "http://localhost:3040/movies?offset=0&limit=10",
        ),
        (
            "http://localhost:3040/movies",
            {},
            "http://localhost:3040/movies",
        ),
    ),
)
def test__add_query_params_to_url(url, query_params, expected_url):
    assert MovieService.add_query_params_to_url(url, query_params) == expected_url


@pytest.mark.parametrize(
    "name,expected_genre",
    (
        ("Action", {"id": 28, "name": "Action"}),
        ("action", None),
        ("TV Movie", {"id": 10770, "name": "TV Movie"}),
        ("TV+Movie", None),
    ),
)
def test__get_genre(name, expected_genre):
    assert get_genre(name) == expected_genre


class FakeResponse:
    def __init__(
        self, response: Optional[dict] = None, status_code: Optional[int] = None
    ) -> None:
        self._response = response
        self.status_code = status_code
        self.text = "Internal Server Error"

    def json(self):
        return self._response


class FakeRequestClient:
    def __init__(self, responses: List[FakeResponse] = None) -> None:
        self._responses = responses
        self.url = None
        self.data = None
        self.called = 0

    def get(self, url: str, data: Optional[dict] = None) -> FakeResponse:
        self.url = url
        self.data = data
        self.called += 1

        response = (
            self._responses.pop(0) if len(self._responses) > 1 else self._responses[0]
        )

        return response


@pytest.mark.parametrize(
    "genre_name,offset,limit,expected_url",
    (
        (
            "Action",
            0,
            10,
            "http://localhost:3040/movies?genre=Action&offset=0&limit=10",
        ),
        ("Action", None, 0, "http://localhost:3040/movies?genre=Action&limit=0"),
        ("Action", 0, None, "http://localhost:3040/movies?genre=Action&offset=0"),
        ("Action", None, None, "http://localhost:3040/movies?genre=Action"),
        (None, 0, 10, "http://localhost:3040/movies?offset=0&limit=10"),
        (None, None, None, "http://localhost:3040/movies"),
    ),
)
def test__MovieService__list_ids__200(
    genre_name, offset, limit, expected_url, movies_ids
):
    client = FakeRequestClient(
        responses=[FakeResponse(response={"data": movies_ids}, status_code=200)]
    )
    service = MovieService(client=client)
    genre = get_genre(genre_name)

    assert service.list_ids(genre, offset, limit) == movies_ids
    assert client.url == expected_url


def test__MovieService__list_ids__500_at_first_attempt(movies_ids):
    client = FakeRequestClient(
        responses=[
            FakeResponse(response=None, status_code=500),
            FakeResponse(response={"data": movies_ids}, status_code=200),
        ]
    )
    service = MovieService(client=client)
    genre = get_genre("Action")

    assert service.list_ids(genre) == movies_ids
    assert client.called == 2


@pytest.mark.xfail
def test__MovieService__get_details__200_all_details(movies_ids, movies_details):
    client = FakeRequestClient(
        responses=[
            FakeResponse(
                response={"data": movies_details},
                status_code=200,
            )
        ]
    )

    assert MovieService(client).get_details(movies_ids) == movies_details


@pytest.mark.parametrize(
    "list_,max_length,expected",
    (
        (
            [1, 2, 3, 4, 5, 6, 7, 8, 9],
            3,
            [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
        ),
        (
            [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            3,
            [[1, 2, 3], [4, 5, 6], [7, 8, 9], [10]],
        ),
    ),
)
def test__split_list_with_max_lenght(list_, max_length, expected):
    assert InterfaceService.split_list_with_max_length(list_, max_length) == expected
