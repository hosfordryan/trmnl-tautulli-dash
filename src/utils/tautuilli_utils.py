from datetime import datetime
import logging
from zoneinfo import ZoneInfo
import requests

from ..config import Config

logger = logging.getLogger(__name__)


def get_tautilli_endpoint(command: str, args: list):
    tautilli_api_key = Config.TAUTULLI_API_KEY
    ip = Config.TAUTULLI_IP
    port = Config.TAUTULLI_PORT

    # Shouldn't be None because of the validate classmethod, but the endpoint string concat below doesn't know that
    assert tautilli_api_key is not None

    endpoint = (
        "http://"
        + ip
        + ":"
        + port
        + "/api/v2?apikey="
        + tautilli_api_key
        + "&cmd="
        + command
    )
    if len(args) > 0:
        for name, value in args:
            endpoint += "&" + name + "=" + str(value)
    return endpoint


def get_plays_graph_data():
    request = get_tautilli_endpoint(
        "get_plays_by_date", [("time_range", "30"), ("y_axis", "duration")]
    )
    graph_data = requests.get(request).json()["response"]["data"]
    result = []
    for i, date in enumerate(graph_data["categories"]):
        # row = [date] + [series["data"][i] for series in graph_data["series"]]
        row = [date] + [
            int(series["data"][i]) / 3600 for series in graph_data["series"]
        ]  # Convert seconds data into hours
        result.append(row)
    summed_without_music = [
        [date, series_data[0] + series_data[1]] for date, *series_data in result
    ]
    return summed_without_music


def get_server_name():
    logger.info(f"Request: {get_tautilli_endpoint('get_server_friendly_name', [])}")
    result = requests.get(get_tautilli_endpoint("get_server_friendly_name", [])).json()
    # TODO: Pull out this error handling to be used by every API call
    if result["response"]["result"] == "error":
        logger.error(
            f"Failed getting server name with error message: {result['response']['message']}"
        )
    logger.info(f"get_server_name response: {result}")
    name = result["response"]["data"]
    return name


def parse_play_data(response_data):
    data = []
    for row in response_data["rows"]:
        title = row["title"]
        year = row["year"]
        plays = row["total_plays"]
        last_play = row["last_play"]
        data.append(
            {
                "title": title,
                "year": str(year),
                "plays": str(plays),
                "last_play": datetime.fromtimestamp(
                    int(last_play), tz=ZoneInfo("UTC")
                ).strftime("%Y-%m-%d %I:%M %p"),
                "rating_key": str(row["rating_key"]),
            }
        )
    return data


def get_stats():
    movies_url = get_tautilli_endpoint(
        "get_home_stats",
        [
            ("time_range", 30),
            ("stats_type", "plays"),
            ("stat_id", "top_movies"),
            ("stats_count", "5"),
        ],
    )
    result_json = requests.get(movies_url).json()["response"]["data"]
    movie_data = parse_play_data(result_json)
    tv_url = get_tautilli_endpoint(
        "get_home_stats",
        [
            ("time_range", 30),
            ("stats_type", "plays"),
            ("stat_id", "top_tv"),
            ("stats_count", "5"),
        ],
    )
    result_json = requests.get(tv_url).json()["response"]["data"]
    tv_data = parse_play_data(result_json)
    return (movie_data, tv_data)


# Unused. Images are too small to be readable
# def get_poster(rating_key: str):
#     metadata_url = get_tautilli_endpoint("get_metadata", [("rating_key", rating_key)])
#     guid_list = requests.get(metadata_url).json()["response"]["data"]["guids"]
#     imdb_id = guid_list[0].split("//")[1]
#     url = "https://api.themoviedb.org/3/find/" + imdb_id + "?external_source=imdb_id"
#     headers = {
#         "accept": "application/json",
#         "Authorization": "Bearer INSERT_API_TOKEN_HERE",
#     }
#     poster_path = requests.get(url, headers=headers).json()["movie_results"][0][
#         "poster_path"
#     ]
#     poster_url = "https://image.tmdb.org/t/p/w92" + poster_path
#     print(poster_url)
