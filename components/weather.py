import requests
import config


def get_current_weather(city):
    url = "https://community-open-weather-map.p.rapidapi.com/weather"
    querystring = {"q": city, "units": "metric", "lang": "pl"}

    headers = {
        'x-rapidapi-host': "community-open-weather-map.p.rapidapi.com",
        'x-rapidapi-key': config.RAPID_API_KEY
    }
    response = requests.request("GET", url, headers=headers, params=querystring)
    return response.json()


def get_x_day_forecast(city, days):
    url = "https://community-open-weather-map.p.rapidapi.com/forecast/daily"
    querystring = {"q": city, "cnt": days, "units": "metric", "lang": "pl"}

    headers = {
        'x-rapidapi-host': "community-open-weather-map.p.rapidapi.com",
        'x-rapidapi-key': config.RAPID_API_KEY
    }
    response = requests.request("GET", url, headers=headers, params=querystring)
    return response.json()
