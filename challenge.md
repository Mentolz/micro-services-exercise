# Coding Challenge

Hello and welcome to this coding challenge. In this challenge, you are tasked to build a RESTful endpoint. When finished the endpoint will allow the upstream clients to search for movies given a movie genre, and return details of each found movie.

So let's get to the details, shall we?

## Task
You will be building a Restful endpoint for getting a list of movie ids from a downstream server by providing a valid genre. You will then return full details of each movie found by merging responses from some downstream services.

## Acceptance Criteria

### Request
The endpoint definition is:

    GET /movies?genre=Science+Fiction&offset=0&limit=10

`genre`: Matches the genre of the movie. Only single genre is allowed.

`offset`: Provides the starting index for the search results. Default is 0, if not specified.

`limit`: Provides the number of results returned per page. Default is 10 if not specified.

### Response:

The response should be in the below form:

``` json
{
    "data": {
        "movies": [
            {
                "id": "1893",
                "title": "Star Wars: Episode I - The Phantom Menace",
                "releaseYear": 1999,
                "revenue": "US$ 924,317,558",
                "posterPath": "https://image.tmdb.org/t/p/w342/n8V09dDc02KsSN6Q4hC2BX6hN8X.jpg",
                "genres": ["Adventure", "Action", "Science Fiction"],
                "cast": [{
                    "id": "3896",
                    "gender": "Male",
                    "name": "Liam Neeson",
                    "profilePath": "https://image.tmdb.org/t/p/w185/9mdAohLsDu36WaXV2N3SQ388bvz.jpg" 
                    }, ...
                ]
            }, ...
        ]
    },
    "metadata": {
        "offset": 0,
        "limit": 10,
        "total": 20
    },
    "errors": [
        { 
            "errorCode": 440, 
            "message": "Movie id #1000 cast info is not complete"
        },
        { 
            "errorCode": 450, 
            "message": "Movie id #1002 details can not be retrieved"
        }
    ]
}
```
* The genres are provided as a static resource in the `genres.json` file. You can either read it or hardcode them in the app.
* Some of the fields in the response are different than what you receive as raw info from the downstream services. (e.g. `releaseYear` vs. `releaseDate`, `id`s are strings, ... etc.)

### Error Handling:

* Response can have missing cast info (partial response) for some of the movie details. (e.g. failing artist-info service downstream) If that is the case, it should appear in `errors` but still return whatever is available with HTTP 200 status code. (See errorCode: 440 above)
* Response can have missing movie details (partial response), apart from the `id`. (e.g. failing movie-info service downstream) If that is the case, it should appear in `errors` but still return whatever is available with HTTP 200 status code. (See errorCode: 450 above)
* Your endpoint should have a retry mechanism to handle the random 500 errors coming from the downstream service. Please assume the failure rate is unknown.

## Things to remember

* We will be evaluating your pull request based on the rubric that we provided in the `rubric.md` file here. Treat this as a production codebase.
* Make sure you have tests, though end-to-end testing is not required.
* Please keep it simple, only implement what is asked here. Nothing less, nothing more.
* Please DO NOT publish your solutions on a public facing profile. These coding challenges are intended for internal XING interview processes.
* We will delete this repository once the final interview process is done.

# How it works?

You can implement this challenge in one of the following languages - Ruby, Java, Kotlin, Scala, PHP - depending on the position you are applying for. The choice of frameworks etc. are up to you.

When you are ready, you need to send us a pull request. Our reviewers will review your pull request, give you feedback comments (sometimes you may be required to do some changes), and if all goes well merge your pull request and invite you to next stage of interviews. 

We provided you with a `docker-compose.yml` file that has all the downstream services you would need to use to get the data you need.

* Please (if not already) install [Docker for Mac](https://docs.docker.com/docker-for-mac/install/) or if you are on Windows: [Docker for Windows](https://docs.docker.com/docker-for-windows/install/)
* Once you clone this repo on your local machine run `docker-compose up` in your terminal window. This will download the necessary containers and bring the services up.
* When you are done, you can run `docker-compose down` to stop all the containers.

# The "Downstream" services
The failure percent of the services are not meant to be used in the app, they're only there to simulate failures in downstream dependencies.

## Movie-Search Service
This service allows you search for movies based on genre and revenue.

`Service Address`: http://localhost:3040

`Git Repository` : https://github.com/keremk/movie-search

`Failure Percent` : This service can fail 10% of the time.

## Movie-Info Service
This service gives you detailed movie info.

`Service Address`: http://localhost:3030

`Git Repository` : https://github.com/keremk/movie-info

`Max Allowed Batch Size`: This service allows you to request a batch of maximum 5 items (through the ids query param). 

`Failure Percent` : This service can fail 20% of the time.

## Artist-Info Service
This service gives you detailed artist info.

`Service Address`: http://localhost:3050

`Git Repository` : https://github.com/keremk/artist-info

`Max Allowed Batch Size`: This service allows you to request a batch of maximum 5 items (through the ids query param). 

`Failure Percent` : This service can fail 50% of the time. Really flaky one!
