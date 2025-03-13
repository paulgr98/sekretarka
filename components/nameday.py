import json

import requests

country = 'pl'
url = "https://nameday.abalin.net/api/V2/today"


def get_names():
    response = requests.get(url)
    data = json.loads(response.text)
    names_string = data['data'][country]
    names_string = names_string.replace(' ', '')
    names = names_string.split(',')
    return names
