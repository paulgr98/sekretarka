import random
from dataclasses import dataclass
from typing import Optional

import requests


@dataclass
class ErgastResponse(object):
    """
    makes the request to the api
    url: [str] request url
    offset: [int] starting point of elements from API request
    limit: [int] number of items to return per request
    """

    url: str
    offset: Optional[int] = None
    limit: Optional[int] = None
    _json = None
    _text = None

    def make_request(self):
        self.url = f"{self.url}"
        if self.limit and self.offset:
            querystring = {"limit": self.limit, "offset": self.offset}
        else:
            querystring = None
        return requests.get(self.url, params=querystring)

    @property
    def json(self):
        if self._json is None:
            self._json = self.make_request()
        return self._json.json()


@dataclass
class F1(object):
    secure: Optional[bool] = True
    offset: Optional[int] = None
    limit: Optional[int] = None

    __all__ = {
        "all_drivers": "drivers",
        "all_circuits": "circuits",
        "all_seasons": "seasons",
        "current_schedule": "current",
        "season_schedule": "{season}",
        "all_constructors": "constructors",
        "race_standings": "{season}/driverStandings",
        "constructor_standings": "{season}/constructorStandings",
        "driver_season": "{season}/drivers",
    }

    def __getattr__(self, attr):
        path = self.__all__.get(attr)
        if path is None:
            raise AttributeError

        def outer(path):
            def inner(**kwargs):
                url = self._build_url(path, **kwargs)
                return ErgastResponse(url)

            return inner

        return outer(self.__all__[attr])

    def random(self, **kwargs):
        applicable_actions = []
        for action in self.__all__.keys():
            applicable_actions.append(action)
        choice = getattr(self, random.choice(applicable_actions))
        return choice(**kwargs)

    def _build_url(self, path, **kwargs) -> str:
        url = "{protocol}://api.jolpi.ca/ergast/f1/{path}".format(
            protocol="https" if self.secure else "http", path=path.format(**kwargs)
        )
        return url


f1 = F1()
