from urllib.parse import unquote

from app.schemas import CastMember, Movie
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
def test__BaseService__add_query_params_to_url(url, query_params, expected_url):
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
def test__BaseService__get_genre(name, expected_genre):
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
def test__BaseService__split_list_with_max_lenght(list_, max_length, expected):
    assert BaseService.split_list_with_max_length(list_, max_length) == expected


def test__BaseService__request_unitl_status_code_is_200():
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
def test__BaseService__get_details_url(ids, url, expected_url):
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
def test__BaseService__filter(list_, offset, limit, expected_result):
    assert BaseService.filter(list_, offset, limit) == expected_result


def test__CastService__get_details__incomplete_cast_details(vin_disiel):
    cast_ids = [1, 2, 3, 4, 5, 6]

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


def test__CastService__get_details__full_cast_details(vin_disiel):
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
        vin_disiel,
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


def test__MovieService___build_details_from_response():
    mid = "movie-id-1"
    fake_response = [MovieService.MovieDetailsResponse(id=mid)]
    movie_service = MovieService(client=None)
    movies = movie_service._build_details_from_response(response=fake_response)
    assert movies == [Movie(id=mid)]
    assert movie_service.errors == [
        {"errorCode": 440, "message": "Movie id #movie-id-1 cast info is not complete"}
    ]


def test__MovieService__get_details__couldnt_get_details(mocker):
    mocker.patch("app.services.MovieService._request_details", return_value=None)

    movie_service = MovieService(client=None)

    movies_ids = [1, 2, 3]
    movies = movie_service.get_details(movies_ids)
    assert movies == [
        Movie(
            id="1",
            title=None,
            releaseYear=None,
            revenue=None,
            posterPath=None,
            genres=None,
            cast=None,
        ),
        Movie(
            id="2",
            title=None,
            releaseYear=None,
            revenue=None,
            posterPath=None,
            genres=None,
            cast=None,
        ),
        Movie(
            id="3",
            title=None,
            releaseYear=None,
            revenue=None,
            posterPath=None,
            genres=None,
            cast=None,
        ),
    ]
    assert movie_service.errors == [
        {"errorCode": 450, "message": "Movie id #1 details can not be retrieved"},
        {"errorCode": 450, "message": "Movie id #2 details can not be retrieved"},
        {"errorCode": 450, "message": "Movie id #3 details can not be retrieved"},
        {"errorCode": 440, "message": "Movie id #1 cast info is not complete"},
        {"errorCode": 440, "message": "Movie id #2 cast info is not complete"},
        {"errorCode": 440, "message": "Movie id #3 cast info is not complete"},
    ]


def test__MovieService__get_details__for_some_movies(mocker, vin_disiel: CastMember):
    movie_id = "mid-1"
    mocker.patch(
        "app.services.MovieService._request_details",
        side_effect=[
            None,
            [
                MovieService.MovieDetailsResponse(
                    id=movie_id,
                    title="Fast Furious",
                    releaseDate="2020-02-10",
                    revenue=1000000,
                    posterPath="www",
                    genres=[28, 10770],
                    cast=[vin_disiel.id],
                )
            ],
        ],
    )

    mocker.patch("app.services.CastService.get_details", return_value=[vin_disiel])

    movie_service = MovieService(client=None)

    movies_ids = [1, 2, 3, 4, 5, 6]
    movies = movie_service.get_details(movies_ids)
    assert movies == [
        Movie(
            id="1",
            title=None,
            releaseYear=None,
            revenue=None,
            posterPath=None,
            genres=None,
            cast=None,
        ),
        Movie(
            id="2",
            title=None,
            releaseYear=None,
            revenue=None,
            posterPath=None,
            genres=None,
            cast=None,
        ),
        Movie(
            id="3",
            title=None,
            releaseYear=None,
            revenue=None,
            posterPath=None,
            genres=None,
            cast=None,
        ),
        Movie(
            id="4",
            title=None,
            releaseYear=None,
            revenue=None,
            posterPath=None,
            genres=None,
            cast=None,
        ),
        Movie(
            id="5",
            title=None,
            releaseYear=None,
            revenue=None,
            posterPath=None,
            genres=None,
            cast=None,
        ),
        Movie(
            id=movie_id,
            title="Fast Furious",
            releaseYear=2020,
            revenue="US$ 1,000,000",
            posterPath="www",
            genres=["Action", "TV Movie"],
            cast=[vin_disiel],
        ),
    ]
    assert movie_service.errors == [
        {"errorCode": 450, "message": "Movie id #1 details can not be retrieved"},
        {"errorCode": 450, "message": "Movie id #2 details can not be retrieved"},
        {"errorCode": 450, "message": "Movie id #3 details can not be retrieved"},
        {"errorCode": 450, "message": "Movie id #4 details can not be retrieved"},
        {"errorCode": 450, "message": "Movie id #5 details can not be retrieved"},
        {"errorCode": 440, "message": "Movie id #1 cast info is not complete"},
        {"errorCode": 440, "message": "Movie id #2 cast info is not complete"},
        {"errorCode": 440, "message": "Movie id #3 cast info is not complete"},
        {"errorCode": 440, "message": "Movie id #4 cast info is not complete"},
        {"errorCode": 440, "message": "Movie id #5 cast info is not complete"},
    ]
