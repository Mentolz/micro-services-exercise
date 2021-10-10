from pydantic import BaseModel
from typing import Optional, List

from pydantic.fields import Field


class CastMember(BaseModel):
    id: str = Field(..., example="3896")
    gender: str = Field(..., example="Male")
    name: str = Field(..., example="Liam Neeson")
    profilePath: str = Field(
        ..., example="https://image.tmdb.org/t/p/w185/9mdAohLsDu36WaXV2N3SQ388bvz.jpg"
    )


class Movie(BaseModel):
    id: str = Field(..., example="1893")
    title: str = Field(..., example="Star Wars: Episode I - The Phantom Menace")
    releaseYear: int = Field(..., example=1999)
    revenue: str = Field(..., example="US$ 924,317,558")
    posterPath: str = Field(
        ..., example="https://image.tmdb.org/t/p/w342/n8V09dDc02KsSN6Q4hC2BX6hN8X.jpg"
    )
    genres: List[str] = Field(  # TYPING: List[Gender.name]
        None, example=["Adventure", "Action", "Science Fiction"]
    )
    cast: Optional[List[CastMember]]
