from datetime import UTC, datetime
from ..utils.tautuilli_utils import get_server_name, get_stats, get_plays_graph_data
import logging
from typing import Dict, Any
import requests
from ..config import Config

logger = logging.getLogger(__name__)


class TautulliMetricsService:

    def __init__(self):
        self.last_update = None
        self._cached_data = None
        self._cache_timestamp = None

    def build_data_html(self, data):
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

    def get_data(self):
        try:
            if self._is_cache_valid():
                logger.info("Cache is valid. Returned cached data")
                return self._cached_data

            data = self._fetch_data()

            self._update_cache(data)
            self.last_update = datetime.now(UTC)
            return data

        except Exception as e:
            logger.error(f"Error fetching data: {str(e)}", e)

    def _fetch_data(self):
        server_name = get_server_name()
        movie_data, tv_data = get_stats()
        movie_html = self.build_data_html(movie_data)
        tv_html = self.build_data_html(tv_data)
        play_data = get_plays_graph_data()
        logger.info("Got all data.")
        return {
            "server_name": server_name,
            "movie_html": movie_html,
            "tv_html": tv_html,
            "play_data": play_data,
            "success": "true",
        }

    def _send_data(self, data):
        plugin_uuid = Config.TRMNL_PLUGIN_UUID
        assert plugin_uuid is not None
        base_url = "https://usetrmnl.com/api/custom_plugins/"
        url = base_url + plugin_uuid

        try:
            variables = {
                "merge_variables": {
                    "server_name": str(data["server_name"]),
                    "movies_html": data["movie_html"],
                    "tv_html": data["tv_html"],
                    "graph_data": str(data["play_data"]),
                }
            }
            result = requests.post(url, json=variables)
            logger.info(result)
        except requests.exceptions.RequestsWarning as e:
            logger.error("[ERROR] Got Exception during API request: ", e)

    def _update_cache(self, data: Dict[str, Any]) -> None:
        self._cached_data = data
        self._cache_timestamp = datetime.now(UTC)

    def _is_cache_valid(self) -> bool:
        if not self._cache_timestamp:
            return False

        cache_age = (datetime.now(UTC) - self._cache_timestamp).total_seconds()
        return cache_age < Config.CACHE_TIMEOUT_SEC
