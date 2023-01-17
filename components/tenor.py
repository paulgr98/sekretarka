import requests
import config as cfg


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
