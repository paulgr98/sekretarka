import datetime as dt
import discord
from requests import HTTPError
from components.weather import get_current_weather, get_15_day_forecast


class WeatherException(Exception):
    pass


def make_weather_embed(city: str, days: int) -> discord.Embed:
    # create dictionary for each day in Polish and English
    day_dict = {"monday": "Poniedziałek", "tuesday": "Wtorek", "wednesday": "Środa", "thursday": "Czwartek",
                "friday": "Piątek", "saturday": "Sobota", "sunday": "Niedziela"}

    if days == 0:
        try:
            current_weather_json = get_current_weather(city)
        except HTTPError:
            raise WeatherException('Nieprawidłowe miasto')

        # handle errors
        wthr_handle_errors(current_weather_json, city)

        date = dt.datetime.now().strftime('%d.%m.%Y')
        day_of_week = dt.datetime.strptime(date, '%d.%m.%Y').strftime('%A').lower()
        day_of_week_pl = day_dict[day_of_week]

        weather_text = current_weather_json['WeatherText']
        precipitations = current_weather_json['PrecipitationType']
        precipitations = precipitations if precipitations else 'Brak'
        temp = current_weather_json['Temperature']['Metric']['Value']
        feels_like = current_weather_json['RealFeelTemperature']['Metric']['Value']
        humidity = current_weather_json['RelativeHumidity']
        pressure = current_weather_json['Pressure']['Metric']['Value']
        wind_speed = current_weather_json['Wind']['Speed']['Metric']['Value']
        wind_direction = current_weather_json['Wind']['Direction']['Localized']

        embed = discord.Embed(title=f'Pogoda dla {city.title()}, {date} ({day_of_week_pl})', color=0x066FBF)
        embed.add_field(name='Opis', value=weather_text, inline=False)
        embed.add_field(name='Temperatura', value=f'Aktualna: {float(temp):.1f} °C\n '
                                                  f'Odczuwalna: {float(feels_like):.1f} °C', inline=False)
        embed.add_field(name='Opady', value=precipitations, inline=False)
        embed.add_field(name='Ciśnienie', value=f'{pressure} hPa', inline=False)
        embed.add_field(name='Wilgotność', value=f'{humidity}%', inline=False)
        embed.add_field(name='Wiatr', value=f'Szybkość: {wind_speed} km/h\nKierunek: {wind_direction}', inline=False)
    else:
        try:
            day_weather_json = get_15_day_forecast(city)
        except HTTPError:
            raise WeatherException('Nieprawidłowe miasto')

        wthr_handle_errors(day_weather_json, city)

        day = day_weather_json['DailyForecasts'][days]

        date = dt.datetime.fromtimestamp(day["EpochDate"]).strftime('%d.%m.%Y')
        day_of_week = dt.datetime.strptime(date, '%d.%m.%Y').strftime('%A').lower()
        day_of_week_pl = day_dict[day_of_week]

        sun_rise = day['Sun']['Rise']
        sun_set = day['Sun']['Set']
        sun_rise = dt.datetime.strptime(sun_rise, '%Y-%m-%dT%H:%M:%S+01:00').strftime('%H:%M')
        sun_set = dt.datetime.strptime(sun_set, '%Y-%m-%dT%H:%M:%S+01:00').strftime('%H:%M')

        temp_min = day['Temperature']['Minimum']['Value']
        temp_max = day['Temperature']['Maximum']['Value']
        feels_like_max = day['RealFeelTemperature']['Maximum']['Value']
        description = day['Day']['IconPhrase']
        wind_speed = day['Day']['Wind']['Speed']['Value']
        wind_direction = day['Day']['Wind']['Direction']['Localized']
        has_precipitation = day['Day']['HasPrecipitation']
        if has_precipitation:
            precipitation_type = day['Day']['PrecipitationType']
            precipitation_intensity = day['Day']['PrecipitationIntensity']
        else:
            precipitation_type = 'Brak opadów'
            precipitation_intensity = ''

        embed = discord.Embed(title=f'Pogoda dla {city.title()}, {date} ({day_of_week_pl})', color=0x066FBF)
        embed.add_field(name='Opis', value=description, inline=False)
        embed.add_field(name='Temperatura', value=f'Maksymalna: {float(temp_max):.1f} °C\n'
                                                  f'Minimalna: {float(temp_min):.1f} °C\n'
                                                  f'Odczuwalna: {float(feels_like_max):.1f} °C', inline=False)
        embed.add_field(name='Opady', value=f'{precipitation_type} {precipitation_intensity}', inline=False)
        embed.add_field(name='Wiatr', value=f'Szybkość: {wind_speed} km/h\nKierunek: {wind_direction}', inline=False)
        embed.add_field(name='Słońce', value=f'Wschód: {sun_rise}\nZachód: {sun_set}', inline=False)

    return embed


def wthr_handle_errors(wthr_json: dict, city: str) -> None:
    if 'cod' in wthr_json:
        if wthr_json['cod'] in [404, 400]:
            raise WeatherException(f'Nie znaleziono miasta {city}')
        if wthr_json['cod'] == 429:
            raise WeatherException('Przekroczono limit zapytań do API')
        if wthr_json['cod'] == 401:
            raise WeatherException('Nieprawidłowy klucz API')
