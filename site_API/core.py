# site_API\core.py
import requests


class SiteApi:
    """
    Provides an interface to interact with the UNOGs (Unofficial Netflix Online Global Search) API to retrieve movie
    and series data based on various search criteria.
    """
    def __init__(self, SITE_API: str, HOST_API: str):
        """
        Initializes the SiteApi object with necessary API credentials and default search parameters.

        :param SITE_API: API key for accessing the UNOGs API.
        :param HOST_API: Host name for the UNOGs API.
        """
        self.url = "https://unogsng.p.rapidapi.com/search"

        self.params = {"orderby": "rating",
                       "limit": "5",
                       "audio": "english",
                       "offset": "1",
                       "type": "movie"}

        self.headers = {"X-RapidAPI-Key": SITE_API, "X-RapidAPI-Host": HOST_API}

    def set_choice(self, choice: str):
        """
        Sets the type of content to search for in the API (either 'movie' or 'series').

        :param choice: The type of content ('movie' or 'series').
        """
        self.params["type"] = choice

    def set_lim(self, lim: str):
        """
        Sets the limit of results to return from the API.

        :param lim: The maximum number of results to retrieve.
        """
        self.params["limit"] = lim

    def set_low(self, low: str):
        """
        Sets the lower boundary for the movie/series ratings.

        :param low: The lowest rating to include in search results.
        """
        self.params["start_rating"] = low

    def _set_high(self, high: str):
        """
        Sets the upper boundary for the movie/series ratings.

        :param high: The highest rating to include in search results.
        """
        self.params["end_rating"] = high

    def get_high(self):
        """
        Retrieves items without any specific rating boundary filters. Resets any previously set rating filters.

        :return: JSON response containing high-rated movies or series.
        """
        if "end_rating" in self.params:
            self.params.pop("end_rating")
        if "start_rating" in self.params:
            self.params.pop("start_rating")

        response = requests.get(self.url, headers=self.headers, params=self.params)

        return response.json()

    def get_low(self):
        """
        Retrieves items rated from 0 to 4. Uses predefined methods to set the rating boundaries.

        :return: JSON response containing low-rated movies or series.
        """
        self.set_low("0")
        self._set_high("4")

        response = requests.get(self.url, headers=self.headers, params=self.params)

        return response.json()

    def get_custom(self, high: str):
        """
        Retrieves items up to a custom highest rating set by the user.

        :param high: The highest rating to include in the search.
        :return: JSON response containing movies or series up to the specified rating.
        """
        self._set_high(high)

        response = requests.get(self.url, headers=self.headers, params=self.params)

        return response.json()