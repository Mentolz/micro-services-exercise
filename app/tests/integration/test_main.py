from app.services import MovieService
from app.tests.entities import FakeRequestClient, FakeResponse
from app.tests.movies_details_example import (
    CAST_RAW,
    MOVIES_DETAILS_COMPLETED,
    MOVIES_DETAILS_RAW,
    MOVIES_IDS,
)


def test__list_movies(mocker, client):
    total = len(MOVIES_IDS) 
    limit = 10
    offset = 0

    fake_client = FakeRequestClient(
        responses=[
            FakeResponse(status_code=200, response={"data": MOVIES_IDS}),
            FakeResponse(status_code=200, response={"data": MOVIES_DETAILS_RAW}),
            FakeResponse(status_code=200, response={"data": CAST_RAW[0]}),
            FakeResponse(status_code=200, response={"data": CAST_RAW[1]}),
        ]
    )

    mocker.patch("app.main.MovieService", return_value=MovieService(fake_client))

    response = client.get(f"/movies?genre=Action&offset={offset}&limit={limit}")

    assert response.status_code == 200
    assert response.json() == {
        "data": {"movies": MOVIES_DETAILS_COMPLETED},
        "metadata": {"offset": offset, "limit": total, "total": total},
        "errors": None,
    }
