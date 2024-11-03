import io

import requests

from config import config as cfg


class Tenor(object):
    def __init__(self):
        self.api_key = cfg.TENOR_API_KEY
        self.base_url = 'https://tenor.googleapis.com/v2/search?'

    def get_gif(self, search_term: str = '', random: bool = True) -> str:
        url = f'{self.base_url}q="{search_term}"&random={str(random).lower()}&key={self.api_key}&limit=1'
        response = requests.get(url)
        response.raise_for_status()
        if response.status_code == 200:
            return response.json()['results'][0]['media_formats']['gif']['url']
        else:
            return ''


def url_to_file(url: str) -> io.BytesIO:
    try:
        req = requests.get(url)
        req.raise_for_status()
        return io.BytesIO(req.content)
    except Exception:
        return io.BytesIO()
