import pytest
from typing import List

from app.tests.movies_details_example import (
    MOVIES_DETAILS_COMPLETED,
    MOVIES_DETAILS_WITH_CAST_IDS,
)


@pytest.fixture
def movies_ids() -> List[int]:
    return [1893, 1724, 955, 24, 485942]


@pytest.fixture
def movies_details_with_cast_ids() -> dict:
    return MOVIES_DETAILS_WITH_CAST_IDS


@pytest.fixture
def movies_details() -> dict:
    return MOVIES_DETAILS_COMPLETED
