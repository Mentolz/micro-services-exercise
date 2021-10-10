from urllib.parse import unquote

from pydantic import errors
from app.schemas import CastMember
from app.services import BaseService, CastService, MovieService, get_genre
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
    assert BaseService.split_list_with_max_length(list_, max_length) == expected


def test__request_unitl_status_code_is_200():
    client = FakeRequestClient(
        responses=[
            FakeResponse(status_code=500),
            FakeResponse(status_code=500),
            FakeResponse(status_code=200),
            FakeResponse(status_code=500),
        ]
    )
    BaseService.request_until_status_code_is_200(client, url="")
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
    assert unquote(BaseService.get_details_url(ids, url)) == expected_url


@pytest.mark.parametrize(
    "list_,offset,limit,expected_result",
    (
        (
            [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            0,
            5,
            [1, 2, 3, 4, 5],
        ),
        (
            [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            5,
            5,
            [6, 7, 8, 9, 10],
        ),
        (
            [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            5,
            10,
            [6, 7, 8, 9, 10],
        ),
    ),
)
def test__filter(list_, offset, limit, expected_result):
    assert MovieService.filter(list_, offset, limit) == expected_result


def test__CastService__get_details__incomplete_cast_details():
    cast_ids = [1, 2, 3, 4, 5, 6]
    vin_disiel = CastMember(
        id=6,
        gender="M",
        name="Vin Disiel",
        profilePath="www",
    )

    client = FakeRequestClient(
        responses=[
            FakeResponse(status_code=500),
            FakeResponse(
                status_code=200,
                response={
                    "data": [
                        {
                            "id": vin_disiel.id,
                            "gender": vin_disiel.gender,
                            "name": vin_disiel.name,
                            "profilePath": vin_disiel.profilePath,
                        }
                    ]
                },
            ),
        ]
    )
    cast_service = CastService(client)
    details = cast_service.get_details(cast_ids)
    assert details == [vin_disiel]
    assert cast_service.errors


def test__CastService__get_details__full_cast_details():
    cast_ids = [1, 2, 3, 4, 5, 6]

    expected_result = [
        CastMember(
            id=1,
            gender="M",
            name="Paul Walker",
            profilePath="www.paul-walker.com",
        ),
        CastMember(
            id=2,
            gender="F",
            name="Jordana Brewster",
            profilePath="www.jordana-brewster.com",
        ),
        CastMember(
            id=3,
            gender="F",
            name="Michelle Rodriguez",
            profilePath="www.michelle.com",
        ),
        CastMember(
            id=4,
            gender="F",
            name="Gal Gadot",
            profilePath="www.gal-gadot.com",
        ),
        CastMember(
            id=5,
            gender="M",
            name="Dwayne Johnson",
            profilePath="www.dwayne-johnson.com",
        ),
        CastMember(
            id=6,
            gender="M",
            name="Vin Disiel",
            profilePath="www.vindisel-profile.com",
        ),
    ]

    client = FakeRequestClient(
        responses=[
            FakeResponse(
                status_code=200,
                response={
                    "data": [
                        {
                            "id": member.id,
                            "gender": member.gender,
                            "name": member.name,
                            "profilePath": member.profilePath,
                        }
                        for member in expected_result[:5]
                    ]
                },
            ),
            FakeResponse(
                status_code=200,
                response={
                    "data": [
                        {
                            "id": member.id,
                            "gender": member.gender,
                            "name": member.name,
                            "profilePath": member.profilePath,
                        }
                        for member in expected_result[5:]
                    ]
                },
            ),
        ]
    )
    cast_service = CastService(client)
    details = cast_service.get_details(cast_ids)
    assert details == expected_result
    assert not cast_service.errors
