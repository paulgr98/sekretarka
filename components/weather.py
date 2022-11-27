import requests
import config

def get_location_key(city):
    url = 'http://dataservice.accuweather.com/locations/v1/cities/search'

    query_params = {
        'apikey': config.ACCUWEATHER_API_KEY,
        'q': city,
        'language': 'pl-pl',
        'details': 'true'
    }

    location_response = requests.get(url, params=query_params)
    location_response.raise_for_status()

    # check if location exists
    if not location_response.json():
        return {'cod': '404', 'message': 'city not found'}

    location = location_response.json()[0]
    location_key = location['Key']
    return location_key

def get_current_weather(city):
    # OLD FOR OPEN WEATHER MAP
    # url = "https://api.openweathermap.org/data/2.5/weather"
    # url = 'https://community-open-weather-map.p.rapidapi.com/weather'
    # querystring = {"q": city, "units": "metric", "lang": "pl"}

    # headers = {
    #     'x-rapidapi-host': "community-open-weather-map.p.rapidapi.com",
    #     'x-rapidapi-key': config.RAPID_API_KEY
    # }
    # response = requests.request("GET", url, headers=headers, params=querystring)
    # return response.json()

    # NEW FOR ACCUWEATHER
    location_key = get_location_key(city)

    current_conditions_url = f'http://dataservice.accuweather.com/currentconditions/v1/{location_key}'

    query_params = {
        'apikey': config.ACCUWEATHER_API_KEY,
        'language': 'pl-pl',
        'details': 'true'
    }

    current_conditions_response = requests.get(current_conditions_url, params=query_params)
    current_conditions_response.raise_for_status()
    current_conditions = current_conditions_response.json()[0]
    return current_conditions


def get_15_day_forecast(city):
    # OLD FOR OPEN WEATHER MAP
    # url = "https://community-open-weather-map.p.rapidapi.com/forecast/daily"
    # querystring = {"q": city, "cnt": days, "units": "metric", "lang": "pl"}
    #
    # headers = {
    #     'x-rapidapi-host': "community-open-weather-map.p.rapidapi.com",
    #     'x-rapidapi-key': config.RAPID_API_KEY
    # }
    # response = requests.request("GET", url, headers=headers, params=querystring)
    # return response.json()

    # NEW FOR ACCUWEATHER
    location_key = get_location_key(city)

    forecast_url = f'http://dataservice.accuweather.com/forecasts/v1/daily/5day/{location_key}'

    query_params = {
        'apikey': config.ACCUWEATHER_API_KEY,
        'language': 'pl-pl',
        'details': 'true',
        'metric': 'true'
    }

    forecast_response = requests.get(forecast_url, params=query_params)
    forecast_response.raise_for_status()
    forecast = forecast_response.json()
    return forecast

