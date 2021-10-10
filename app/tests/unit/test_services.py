from urllib.parse import unquote
from app.services import InterfaceService, MovieService, get_genre
import pytest
from app.tests.entities import FakeRequestClient, FakeResponse


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


@pytest.mark.xfail
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


def test__request_unitl_status_code_is_200():
    client = FakeRequestClient(
        responses=[
            FakeResponse(status_code=500),
            FakeResponse(status_code=500),
            FakeResponse(status_code=200),
            FakeResponse(status_code=500),
        ]
    )
    InterfaceService.request_until_status_code_is_200(client, url="")
    assert client.called == 3


@pytest.mark.parametrize(
    "ids,url,expected_url",
    (
        (
            [1, 2, 3],
            "http://localhost:3040/movies",
            "http://localhost:3040/movies?ids=1,2,3",
        ),
        (
            [1],
            "http://localhost:3040/movies",
            "http://localhost:3040/movies?id=1",
        ),
    ),
)
def test__get_details_url(ids, url, expected_url):
    assert unquote(InterfaceService.get_details_url(ids, url)) == expected_url
