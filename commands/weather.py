import datetime as dt
from typing import Optional

import discord
from discord import Embed
from requests import HTTPError

from bot.logger import logger
from components.weather import get_current_weather, get_5_day_forecast


class WeatherException(Exception):
    pass


WEATHER_CODES = {
    0: "Czyste niebo",
    1: "W większości czyste niebo",
    2: "Częściowo pochmurnie",
    3: "Pochmurnie",
    45: "Mgła",
    48: "Mgła szronowa",
    51: "Lekka mżawka",
    53: "Umiarkowana mżawka",
    55: "Intensywna mżawka",
    56: "Lekka marznąca mżawka",
    57: "Intensywna marznąca mżawka",
    61: "Lekki deszcz",
    63: "Umiarkowany deszcz",
    65: "Intensywny deszcz",
    66: "Lekki marznący deszcz",
    67: "Intensywny marznący deszcz",
    71: "Lekki śnieg",
    73: "Umiarkowany śnieg",
    75: "Intensywny śnieg",
    77: "Ziarenka śniegu",
    80: "Lekkie przelotne opady deszczu",
    81: "Umiarkowane przelotne opady deszczu",
    82: "Gwałtowne przelotne opady deszczu",
    85: "Lekkie przelotne opady śniegu",
    86: "Intensywne przelotne opady śniegu",
    95: "Lekka lub umiarkowana burza",
    96: "Lekka burza z gradem",
    99: "Intensywna burza z gradem",
}


def get_weather_description(code: int) -> str:
    if code not in WEATHER_CODES:
        raise ValueError(f"Unknown weather code: {code}")
    return WEATHER_CODES[code]


def make_weather_embed(city: str, days: Optional[int]) -> discord.Embed:
    day_dict = {"monday": "Poniedziałek", "tuesday": "Wtorek", "wednesday": "Środa", "thursday": "Czwartek",
                "friday": "Piątek", "saturday": "Sobota", "sunday": "Niedziela"}

    if days is None:
        embed = make_current_weather_embed(city, day_dict)
    else:
        embed = make_future_weather_embed(city, day_dict, days)

    return embed


def make_current_weather_embed(city: str, day_dict: dict[str, str]) -> Embed:
    wthr_json = None
    try:
        wthr_json = get_current_weather(city)
    except HTTPError as exc:
        handle_errors(exc)

    date = dt.datetime.now().strftime('%d.%m.%Y')
    day_of_week = dt.datetime.strptime(date, '%d.%m.%Y').strftime('%A').lower()
    day_of_week_pl = day_dict[day_of_week]

    description = get_weather_description(wthr_json["current"]["weather_code"])

    current_temp = f'Aktualna: {wthr_json["current"]["temperature_2m"]} °C'
    apparent_temp = f'Odczuwalna: {wthr_json["current"]["apparent_temperature"]} °C'
    temp = f'{current_temp}\n{apparent_temp}'

    precipitation_amount: float = wthr_json["current"]["precipitation"]
    precipitation_text = f'{precipitation_amount} mm'
    precipitation = f'{precipitation_text if precipitation_amount > 0.01 else "Brak"}'

    pressure = f'{round(wthr_json["current"]["surface_pressure"])} hPa'

    humidity = f'{wthr_json["current"]["relative_humidity_2m"]}%'

    wind_speed = f'Prędkość: {wthr_json["current"]["wind_speed_10m"]} km/h'
    wind_direction = f'Kierunek: {get_wind_direction(wthr_json["current"]["wind_direction_10m"])}'
    wind = f'{wind_speed}\n{wind_direction}'

    embed = discord.Embed(title=f'Pogoda dla {city.title()}, {date} ({day_of_week_pl})', color=0x066FBF)
    embed.add_field(name="Opis", value=description, inline=False)
    embed.add_field(name="Temperatura", value=temp, inline=False)
    embed.add_field(name="Opady", value=precipitation, inline=False)
    embed.add_field(name="Ciśnienie", value=pressure, inline=False)
    embed.add_field(name="Wilgotność", value=humidity, inline=False)
    embed.add_field(name="Wiatr", value=wind, inline=False)

    return embed


def make_future_weather_embed(city: str, day_dict: dict[str, str], day_num: int) -> Embed:
    wthr_json = None
    try:
        wthr_json = get_5_day_forecast(city)
    except HTTPError as exc:
        handle_errors(exc)

    date = dt.datetime.fromisoformat(wthr_json["daily"]["time"][day_num]).strftime('%d.%m.%Y')
    day_of_week = dt.datetime.strptime(date, '%d.%m.%Y').strftime('%A').lower()
    day_of_week_pl = day_dict[day_of_week]

    description = get_weather_description(wthr_json["daily"]["weather_code"][day_num])

    max_temp = f'Maksymalna: {wthr_json["daily"]["temperature_2m_max"][day_num]} °C'
    min_temp = f'Minimalna: {wthr_json["daily"]["temperature_2m_min"][day_num]} °C'
    temp = f'{min_temp}\n{max_temp}'

    precipitation_amount: float = wthr_json["daily"]["precipitation_sum"][day_num]
    precipitation_amount_text = f'Suma: {precipitation_amount} mm'
    precipitation_probability = wthr_json["daily"]["precipitation_probability_max"][day_num]
    precipitation_probability_text = f'Szansa: {precipitation_probability}%'
    precipitation_text = f'{precipitation_amount_text}\n{precipitation_probability_text}'
    precipitation = f'{precipitation_text if precipitation_amount > 0.01 else "Brak"}'

    wind_speed = f'Prędkość: {wthr_json["daily"]["wind_speed_10m_max"][day_num]} km/h'
    wind_direction = f'Kierunek: {get_wind_direction(wthr_json["daily"]["wind_direction_10m_dominant"][day_num])}'
    wind = f'{wind_speed}\n{wind_direction}'

    sunrise_iso = wthr_json["daily"]["sunrise"][day_num]
    sunrise_local = dt.datetime.fromisoformat(sunrise_iso).strftime('%H:%M')
    sunrise = f'Wschód: {sunrise_local}'
    sunset_iso = wthr_json["daily"]["sunset"][day_num]
    sunset_local = dt.datetime.fromisoformat(sunset_iso).strftime('%H:%M')
    sunset = f'Zachód: {sunset_local}'
    uv_index = f'Index UV: {wthr_json["daily"]["uv_index_max"][day_num]}'
    sun = f'{sunrise}\n{sunset}\n{uv_index}'

    embed = discord.Embed(title=f'Pogoda dla {city.title()}, {date} ({day_of_week_pl})', color=0x066FBF)
    embed.add_field(name="Opis", value=description, inline=False)
    embed.add_field(name="Temperatura", value=temp, inline=False)
    embed.add_field(name="Opady", value=precipitation, inline=False)
    embed.add_field(name="Wiatr", value=wind, inline=False)
    embed.add_field(name="Słońce", value=sun, inline=False)

    return embed


def get_wind_direction(wind_direction_in_degrees: float) -> str:
    angle = wind_direction_in_degrees % 360

    directions = [
        "N", "NNE", "NE", "ENE",
        "E", "ESE", "SE", "SSE",
        "S", "SSW", "SW", "WSW",
        "W", "WNW", "NW", "NNW"
    ]

    direction_amount = len(directions)
    direction_coverage = 360 / direction_amount

    index = round(angle / direction_coverage) % direction_amount
    return directions[index]


def handle_errors(exc: HTTPError):
    logger.error(exc)
    raise WeatherException('Nieprawidłowe miasto')
