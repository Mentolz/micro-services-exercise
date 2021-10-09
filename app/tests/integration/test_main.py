import requests

def test__list_movies__200(movies_details):

    requests.get("dev.localhost:8000/movies")