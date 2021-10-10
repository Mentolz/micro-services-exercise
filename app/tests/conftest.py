import pytest
from typing import List
from app.schemas import CastMember
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)

@pytest.fixture
def movies_ids() -> List[int]:
    return [1893, 1724, 955, 24, 485942]


@pytest.fixture
def vin_disiel() -> CastMember:
    return CastMember(
        id=6,
        gender="Male",
        name="Vin Disiel",
        profilePath="www",
    )