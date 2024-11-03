import datetime as dt

import discord
import requests

from config import config as cfg

# astro API config
# https://rapidapi.com/sameer.kumar/api/aztro/
astro_api = "https://sameer-kumar-aztro-v1.p.rapidapi.com/"
astro_api_headers = {
    "X-RapidAPI-Key": cfg.RAPID_API_KEY,
}


class NoSignException(Exception):
    pass


def make_astrology_embed(sign: str) -> discord.Embed:
    sign = sign.lower()
    # signs dictionary with all signs in Polish and their values in English
    sign_dict = {'baran': 'aries', 'byk': 'taurus', 'bliźnięta': 'gemini', 'rak': 'cancer', 'lew': 'leo',
                 'panna': 'virgo', 'waga': 'libra', 'skorpion': 'scorpio', 'strzelec': 'sagittarius',
                 'koziorożec': 'capricorn', 'wodnik': 'aquarius', 'ryby': 'pisces'}
    sign_dict_reversed = {v: k for k, v in sign_dict.items()}

    # check if the sign is in the dictionary
    if sign in sign_dict.keys():
        sign_eng = sign_dict[sign]
    else:
        available_signs = ', '.join(sign_dict.keys())
        raise NoSignException(f'Nie ma takiego znaku \nDostępne znaki: \n{available_signs}')

    # get the horoscope from the API
    querystring = {"sign": sign_eng, "day": "today"}
    response = requests.request("POST", astro_api, headers=astro_api_headers, params=querystring)

    if 'object has no attribute' in response.content.decode('utf-8'):
        raise NoSignException('API się zepsuło, spróbuj ponownie później')

    # translate the horoscope to polish
    translator = None  # TODO: add translator here
    res_json = response.json()
    description = res_json['description']
    description_pl = translator.translate(description, src='en', dest='pl').text
    mood = res_json['mood']
    mood_pl = f"{translator.translate(mood, src='en', dest='pl').text} ({mood})"
    color_pl = translator.translate(res_json['color'], src='en', dest='pl').text
    comp = res_json['compatibility'].lower()
    comp_pl = sign_dict_reversed[comp]

    # create the embed with the horoscope
    today = dt.datetime.now().strftime('%d.%m.%Y')
    embed = discord.Embed(title=f'{sign.upper()} {today}', color=0x5D37E6)
    embed.add_field(name='Opis', value=f'EN:\n{description}\n\nPL:\n{description_pl}', inline=False)
    embed.add_field(name='Kompatybilność', value=str(comp_pl).capitalize(), inline=False)
    embed.add_field(name='Szczęśliwa liczba', value=response.json()['lucky_number'], inline=False)
    embed.add_field(name='Nastrój', value=mood_pl, inline=False)
    embed.add_field(name='Kolor', value=color_pl, inline=False)

    return embed
