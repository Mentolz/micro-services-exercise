from app.schemas import CastMember, Movie


def test__list_movies(mocker, client):
    total = 20
    limit = 10
    offset = 0

    movies = [
        Movie(
            id="ff",
            title="Fast Furious",
            releaseYear=2020,
            revenue="US$ 1,000,000",
            posterPath="www",
            genres=["Action", "TV Movie"],
            cast=[
                {
                    "id": 6,
                    "gender": "Male",
                    "name": "Vin Disiel",
                    "profilePath": "www",
                }
            ],
        ),
        Movie(
            id="jw",
            title="Jhon Wick",
            releaseYear=2020,
            revenue="US$ 1,000,000",
            posterPath="www",
            genres=["Action", "TV Movie"],
            cast=[
                {
                    "id": 6,
                    "gender": "Male",
                    "name": "Vin Disiel",
                    "profilePath": "www",
                },
                CastMember(
                    id="3896",
                    gender="Male",
                    name="Liam Neeson",
                    profilePath="https://image.tmdb.org/t/p/w185/9mdAohLsDu36WaXV2N3SQ388bvz.jpg",
                ),
            ],
        ),
    ]
    mocker.patch("app.services.MovieService.list", return_value=(movies, total))

    response = client.get(f"/movies?genre=Action&offset={offset}&limit={limit}")

    assert response.status_code == 200
    assert response.json() == {
        "data": {
            "movies": [
                {
                    "id": "ff",
                    "title": "Fast Furious",
                    "releaseYear": 2020,
                    "revenue": "US$ 1,000,000",
                    "posterPath": "www",
                    "genres": ["Action", "TV Movie"],
                    "cast": [
                        {
                            "id": "6",
                            "gender": "Male",
                            "name": "Vin Disiel",
                            "profilePath": "www",
                        }
                    ],
                },
                {
                    "id": "jw",
                    "title": "Jhon Wick",
                    "releaseYear": 2020,
                    "revenue": "US$ 1,000,000",
                    "posterPath": "www",
                    "genres": ["Action", "TV Movie"],
                    "cast": [
                        {
                            "id": "6",
                            "gender": "Male",
                            "name": "Vin Disiel",
                            "profilePath": "www",
                        },
                        {
                            "id": "3896",
                            "gender": "Male",
                            "name": "Liam Neeson",
                            "profilePath": "https://image.tmdb.org/t/p/w185/9mdAohLsDu36WaXV2N3SQ388bvz.jpg",
                        },
                    ],
                },
            ]
        },
        "metadata": {"offset": offset, "limit": limit, "total": total},
        "errors": None,
    }


def test__health_check(client):
    assert client.get("/").status_code == 200