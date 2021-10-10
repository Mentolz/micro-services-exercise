MOVIES_DETAILS_RAW = [
    {
        "id": 1893,
        "title": "Star Wars: Episode I - The Phantom Menace",
        "tagline": "Every generation has a legend. Every journey has a first step. Every saga has a beginning.",
        "overview": "Anakin Skywalker, a young slave strong with the Force, is discovered on Tatooine. Meanwhile, the evil Sith have returned, enacting their plot for revenge against the Jedi.",
        "popularity": 22.71543,
        "runtime": 136,
        "releaseDate": "1999-05-19",
        "revenue": 924317558,
        "budget": 115000000,
        "posterPath": "https://image.tmdb.org/t/p/w342/n8V09dDc02KsSN6Q4hC2BX6hN8X.jpg",
        "originalLanguage": "en",
        "genres": [12, 28, 878],
        "cast": [3896, 3061, 524],
    },
    {
        "id": 1724,
        "title": "The Incredible Hulk",
        "tagline": "You'll like him when he's angry.",
        "overview": "Scientist Bruce Banner scours the planet for an antidote to the unbridled force of rage within him: the Hulk. But when the military masterminds who dream of exploiting his powers force him back to civilization, he finds himself coming face to face with a new, deadly foe.",
        "popularity": 22.619048,
        "runtime": 114,
        "releaseDate": "2008-06-12",
        "revenue": 163712074,
        "budget": 150000000,
        "posterPath": "https://image.tmdb.org/t/p/w342/bleR2qj9UluYl7x0Js7VXuLhV3s.jpg",
        "originalLanguage": "en",
        "genres": [878, 28, 12],
        "cast": [819, 882],
    },
]
MOVIES_IDS = [m["id"] for m in MOVIES_DETAILS_RAW]

MOVIES_DETAILS_COMPLETED = [
    {
        "id": "1893",
        "title": "Star Wars: Episode I - The Phantom Menace",
        "releaseYear": 1999,
        "revenue": "US$ 924,317,558",
        "posterPath": "https://image.tmdb.org/t/p/w342/n8V09dDc02KsSN6Q4hC2BX6hN8X.jpg",
        "genres": ["Action", "Adventure", "Science Fiction"],
        "cast": [
            {
                "id": "3896",
                "name": "Liam Neeson",
                "profilePath": "https://image.tmdb.org/t/p/w185/9mdAohLsDu36WaXV2N3SQ388bvz.jpg",
                "gender": "Male",
            },
            {
                "id": "3061",
                "name": "Ewan McGregor",
                "profilePath": "https://image.tmdb.org/t/p/w185/aEmyadfRXTmmR7UW7OXsm5a6smS.jpg",
                "gender": "Male",
            },
            {
                "id": "524",
                "name": "Natalie Portman",
                "profilePath": "https://image.tmdb.org/t/p/w185/rtLTG4yrEcROXhTBGXMrbyiUEC5.jpg",
                "gender": "Female",
            },
        ],
    },
    {
        "id": "1724",
        "title": "The Incredible Hulk",
        "releaseYear": 2008,
        "revenue": "US$ 163,712,074",
        "posterPath": "https://image.tmdb.org/t/p/w342/bleR2qj9UluYl7x0Js7VXuLhV3s.jpg",
        "genres": ["Action", "Adventure", "Science Fiction"],
        "cast": [
            {
                "id": "819",
                "name": "Edward Norton",
                "profilePath": "https://image.tmdb.org/t/p/w185/eIkFHNlfretLS1spAcIoihKUS62.jpg",
                "gender": "Male",
            },
            {
                "id": "882",
                "name": "Liv Tyler",
                "profilePath": "https://image.tmdb.org/t/p/w185/lD2YnrKdnRUvFDMSiK2pw13ZMIB.jpg",
                "gender": "Female",
            },
        ],
    },
]

CAST_RAW = [
    [
        {
            "id": "3896",
            "name": "Liam Neeson",
            "profilePath": "https://image.tmdb.org/t/p/w185/9mdAohLsDu36WaXV2N3SQ388bvz.jpg",
            "gender": 2,
        },
        {
            "id": "3061",
            "name": "Ewan McGregor",
            "profilePath": "https://image.tmdb.org/t/p/w185/aEmyadfRXTmmR7UW7OXsm5a6smS.jpg",
            "gender": 2,
        },
        {
            "id": "524",
            "name": "Natalie Portman",
            "profilePath": "https://image.tmdb.org/t/p/w185/rtLTG4yrEcROXhTBGXMrbyiUEC5.jpg",
            "gender": 1,
        },
    ],
    [
        {
            "id": "819",
            "name": "Edward Norton",
            "profilePath": "https://image.tmdb.org/t/p/w185/eIkFHNlfretLS1spAcIoihKUS62.jpg",
            "gender": 2,
            "movies": [1724, 399174, 194662, 550],
        },
        {
            "id": "882",
            "name": "Liv Tyler",
            "profilePath": "https://image.tmdb.org/t/p/w185/lD2YnrKdnRUvFDMSiK2pw13ZMIB.jpg",
            "gender": 1,
            "movies": [1724, 121, 122, 120],
        },
    ],
]
