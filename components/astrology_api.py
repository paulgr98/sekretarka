import re

import discord
import googletrans
import requests


class NoHoroscopeSignException(Exception):
    pass


class AstrologyApiWrapper:
    def __init__(self):
        self.base_url = "https://horoscope-app-api.vercel.app/api/v1/get-horoscope"
        self.sign_dict_pl_to_en = {'baran': 'aries', 'byk': 'taurus', 'bliźnięta': 'gemini', 'rak': 'cancer',
                                   'lew': 'leo',
                                   'panna': 'virgo', 'waga': 'libra', 'skorpion': 'scorpio', 'strzelec': 'sagittarius',
                                   'koziorożec': 'capricorn', 'wodnik': 'aquarius', 'ryby': 'pisces'}
        self.sign_dict_en_to_pl = {v: k for k, v in self.sign_dict_pl_to_en.items()}
        self.trans = googletrans.Translator()

    def get_sign_in_en(self, sign_name: str) -> str:
        sign_name = sign_name.lower()
        try:
            if sign_name in self.sign_dict_pl_to_en.keys():
                return self.sign_dict_pl_to_en[sign_name]
            elif sign_name in self.sign_dict_en_to_pl.keys():
                return sign_name
            else:
                raise KeyError
        except KeyError:
            raise NoHoroscopeSignException(f'Niepoprawny znak zodiaku: {sign_name}')

    def get_sign_in_pl(self, sign_name: str) -> str:
        try:
            if sign_name in self.sign_dict_en_to_pl.keys():
                return self.sign_dict_en_to_pl[sign_name]
            elif sign_name in self.sign_dict_pl_to_en.keys():
                return sign_name
            else:
                raise KeyError
        except KeyError:
            raise NoHoroscopeSignException(f'Niepoprawny znak zodiaku: {sign_name}')

    def get_daily_horoscope(self, sign: str) -> str:
        sign = self.get_sign_in_en(sign)
        date = "TODAY"
        target_url = f"{self.base_url}/daily?sign={sign}&day={date}"
        response = requests.get(target_url)
        response.raise_for_status()
        data = response.json()["data"]
        return data["horoscope_data"]

    def translate_horoscope_to_pl(self, horoscope: str) -> str:
        return self.trans.translate(horoscope, src='en', dest='pl').text


def __format_text__(text: str) -> str:
    text = re.sub(r'\.([a-zA-Z])', r'. \1', text)
    return text


class HoroscopeMaker:
    def __init__(self):
        self.api = AstrologyApiWrapper()
        self.sign = None
        self.horoscope = None

    def make_horoscope(self, sign: str) -> "HoroscopeMaker":
        self.sign = sign
        self.horoscope = self.api.get_daily_horoscope(sign)
        return self

    def translate(self) -> "HoroscopeMaker":
        if self.horoscope is None:
            self.raise_error(self.translate().__name__)
        self.horoscope = self.api.translate_horoscope_to_pl(self.horoscope)
        self.horoscope = __format_text__(self.horoscope)
        return self

    def get(self) -> str:
        if self.horoscope is None:
            self.raise_error(self.get.__name__)
        return self.horoscope

    def get_embed(self):
        if self.horoscope is None:
            self.raise_error(self.get_embed.__name__)
        sign_pl = self.api.get_sign_in_pl(self.sign)
        embed = discord.Embed(title=f"Horoskop dla znaku {sign_pl.title()}",
                              description=self.horoscope, colour=0x7830db)
        return embed

    def raise_error(self, function_name: str):
        raise ValueError(f"Used {function_name}, but horoscope is None. Make sure to call make_horoscope() first.")


def main():
    api = AstrologyApiWrapper()
    expected = "cancer"
    actual = api.get_sign_in_en("rak")
    assert expected == actual
    actual = api.get_sign_in_en("cancer")
    assert expected == actual

    expected = "rak"
    actual = api.get_sign_in_pl("cancer")
    assert expected == actual
    actual = api.get_sign_in_pl("rak")
    assert expected == actual

    horoscope_maker = HoroscopeMaker()
    horoscope = horoscope_maker.make_horoscope("rak").translate().get()
    print(horoscope)


if __name__ == '__main__':
    main()
