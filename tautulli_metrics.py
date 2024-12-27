import requests
from datetime import datetime
from zoneinfo import ZoneInfo
from pprint import pprint


def get_tautilli_endpoint(command: str, args: list):
    tautilli_api_key = "c5dff99439ad43168cde4c86586cd8f8"
    ip = "192.168.1.62"
    port = "8181"
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


# Unused. Images look bad.
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
    pprint(result_json)
    tv_data = parse_play_data(result_json)
    return (movie_data, tv_data)


def get_server_name():
    result = requests.get(get_tautilli_endpoint("get_server_friendly_name", [])).json()
    name = result["response"]["data"]
    return name


def build_data_html(data):
    final_html = ""
    count = 1
    for item in data:
        html = ""
        html += '<div class="item">'
        html += '<div class="meta">'
        html += '<span class="index">' + str(count) + "</span>"
        html += "</div>"
        html += '<div class="content">'
        html += '<span class="title title--small">' + item["title"]
        if item["year"] != "":
            html += " (" + item["year"] + ")</span>"
        else:
            html += "</span>"
        html += (
            '<span class="description">'
            + item["plays"]
            + " Plays - Last Played "
            + item["last_play"]
            + "</span>"
        )
        html += "</div>"
        html += "</div>"
        final_html += html
        count += 1
    return final_html


def main():
    plugin_uuid = "8ee98b0c-ac2c-4c84-b982-ec910583835e"
    base_url = "https://usetrmnl.com/api/custom_plugins/"
    url = base_url + plugin_uuid

    server_name = get_server_name()
    movie_data, tv_data = get_stats()
    movie_html = build_data_html(movie_data)
    tv_html = build_data_html(tv_data)

    try:
        variables = {
            "merge_variables": {
                "server_name": str(server_name),
                "movies_html": movie_html,
                "tv_html": tv_html,
            }
        }
        result = requests.post(url, json=variables)
        print(result)
    except requests.exceptions.RequestsWarning as e:
        print("[ERROR] Got Exception during API request: ", e)


if __name__ == "__main__":
    main()
