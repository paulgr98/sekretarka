from urllib.error import HTTPError

import requests

API_URL = 'https://api.open-meteo.com/v1/forecast'


def get_city_info(city):
    url = 'https://geocoding-api.open-meteo.com/v1/search'

    query_params = {
        "name": city
    }

    raw_response = requests.get(url, params=query_params)
    raw_response.raise_for_status()

    location_response = raw_response.json()

    if 'results' not in location_response:
        raise HTTPError(url=raw_response.url, code=404, msg=f"City '{city}' not found")

    results = location_response['results']
    if len(results) == 0:
        raise HTTPError(url=raw_response.url, code=404, msg=f"City '{city}' not found")

    city_info: dict = results[0]

    return city_info


def get_current_weather(city):
    city_info = get_city_info(city)
    latitude = city_info['latitude']
    longitude = city_info['longitude']

    query_params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": ["weather_code", "temperature_2m", "apparent_temperature", "precipitation", "surface_pressure",
                    "relative_humidity_2m", "wind_speed_10m", "wind_direction_10m"],
    }

    current_conditions_response = requests.get(API_URL, params=query_params)
    current_conditions_response.raise_for_status()
    current_conditions = current_conditions_response.json()
    return current_conditions


def get_5_day_forecast(city):
    city_info = get_city_info(city)
    latitude = city_info['latitude']
    longitude = city_info['longitude']

    query_params = {
        "latitude": latitude,
        "longitude": longitude,
        "forecast_days": 6,
        "daily": ["weather_code", "temperature_2m_max", "temperature_2m_min", "sunrise", "sunset", "precipitation_sum",
                  "precipitation_probability_max", "wind_speed_10m_max", "wind_direction_10m_dominant", "uv_index_max"],
    }

    forecast_response = requests.get(API_URL, params=query_params)
    forecast_response.raise_for_status()
    forecast = forecast_response.json()
    return forecast


def main():
    city = "Sosnowiec"
    print(get_city_info(city))
    print(get_current_weather(city))
    print(get_5_day_forecast(city))


if __name__ == "__main__":
    main()
