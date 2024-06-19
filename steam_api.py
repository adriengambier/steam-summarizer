import os
import requests
import time


class SteamAPI:

    def __init__(self):
        self.api_key = os.getenv("STEAM_API_KEY")
        # Estimated time to avoid being blocked by the Steam API (200 requests / 5 min)
        self.wait_time_between_calls = 1.5

    def get_all_games(self) -> list[dict]:
        """Returns a list of all game of the Steam store with their name and id """

        MAX_ALLOWED_RESULTS = 50_000
        url = "https://api.steampowered.com/IStoreService/GetAppList/v1/"

        games = []
        have_more_results = True
        last_appid = None
        while have_more_results:
            params = {
                "key": self.api_key,
                "max_results": MAX_ALLOWED_RESULTS,
                "last_appid": last_appid
            }
            response = requests.get(url, params=params)

            if response.status_code != 200:
                print(
                    f"Error: API request failed with status code {response.status_code}"
                )
                break

            data = response.json().get("response", {})

            new_games = data.get("apps", {})

            game_keys = ["appid", "name"]
            if new_games:
                new_games = [{
                    key: game.get(key, 0)
                    for key in game_keys
                } for game in new_games]
                games.extend(new_games)

            have_more_results = data.get("have_more_results", False)
            last_appid = data.get("last_appid", None)

        return games

    def get_reviews_summary(self, game_id: str) -> dict:
        """Returns the number of positive, negative and overall reviews for a game."""

        params = {
            'json': 1,
            'key': self.api_key,
            'language': "english",
            'filter_offtopic_activity': 0,
            # for the summary, we avoid fetching unnecessary reviews
            'num_per_page': 0,
        }
        url = f"https://store.steampowered.com/appreviews/{game_id}"
        response = requests.get(url, params=params)
        data = response.json()

        summary = data.get("query_summary", {})

        summary_keys = ["total_positive", "total_negative", "total_reviews"]
        if summary:
            summary = {key: summary.get(key, 0) for key in summary_keys}
        summary["id"] = game_id

        return summary

    def get_reviews_summaries(self, game_ids: list) -> list:
        """Returns the number of positive, negative and overall reviews for a list of games."""

        summaries = []
        for id in game_ids:
            summary = self.get_reviews_summary(id)
            summaries.append(summary)

            time.sleep(self.wait_time_between_calls)

        return summaries

    def get_reviews(self,
                    game_id: str,
                    desired_count: int,
                    language: str = "english",
                    filter: str = "all") -> list[str]:
        """Returns a list of reviews for a game."""

        MAX_ALLOWED_RESULTS = 100
        url = f'https://store.steampowered.com/appreviews/{game_id}'

        reviews = []
        cursor = "*"
        while len(reviews) < desired_count:
            num_per_page = min(desired_count - len(reviews),
                               MAX_ALLOWED_RESULTS)
            params = {
                'json': 1,
                'key': self.api_key,
                'filter_offtopic_activity': 0,
                'language': language,
                'filter': filter,
                'num_per_page': num_per_page,
                'cursor': cursor
            }
            response = requests.get(url, params=params)
            data = response.json()

            new_reviews = data.get('reviews', [])

            if not new_reviews:
                break  # Exit if no more reviews are available

            reviews.extend([review["review"] for review in new_reviews])
            cursor = data["cursor"]

            time.sleep(self.wait_time_between_calls)

        return reviews
