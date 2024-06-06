# site_API\core.py

import requests


class SiteApi:
    def __init__(self, SITE_API: str, HOST_API: str):
        self.url = "https://unogsng.p.rapidapi.com/search"

        self.params = {"orderby": "rating",
                       "limit": "5",
                       "audio": "english",
                       "offset": "1",
                       "type": "movie"}

        self.headers = {"X-RapidAPI-Key": SITE_API, "X-RapidAPI-Host": HOST_API}

    def set_choice(self, choice: str):
        self.params["type"] = choice

    def get_high(self, limit=5):
        if limit > 10:
            limit = 10
        self.params["limit"] = str(limit)
        if "end_rating" in self.params:
            self.params.pop("end_rating")
            self.params.pop("start_rating")

        response = requests.get(self.url, headers=self.headers, params=self.params)

        return response.json()

    def get_low(self, limit=5):
        if limit > 10:
            limit = 10
        self.params["limit"] = str(limit)
        self.params["start_rating"] = "3"
        self.params["end_rating"] = "5"

        response = requests.get(self.url, headers=self.headers, params=self.params)

        return response.json()

    def get_custom(self, low: float, high: float, limit=5):
        if limit > 10:
            limit = 10
        self.params["limit"] = str(limit)
        self.params["start_rating"] = str(low)
        self.params["end_rating"] = str(high)
