import json

import requests

country = 'pl'
timezone = 'Europe/Warsaw'
url = f"https://nameday.abalin.net/api/V1/today?country={country}&timezone={timezone}"


def get_names():
    response = requests.get(url)
    data = json.loads(response.text)
    names_string = data['nameday'][country]
    names_string = names_string.replace(' ', '')
    names = names_string.split(',')
    return names
