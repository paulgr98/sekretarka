import requests

import config as cfg

url = 'https://free-epic-games.p.rapidapi.com/free'

headers = {
    'x-rapidapi-host': "free-epic-games.p.rapidapi.com",
    'x-rapidapi-key': cfg.RAPID_API_KEY
}


def get_free_games(period):
    if period not in ['current', 'upcoming']:
        raise ValueError('Period must be one of "current", "upcoming"')
    response = requests.request("GET", url, headers=headers)
    return response.json()['freeGames'][period]
