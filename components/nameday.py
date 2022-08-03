import abalin_nameday
import json

client = abalin_nameday.namedayRequestor(country='pl', timezone='Europe/Warsaw')


def get_names():
    names_string = json.loads(client.GetData())['namedays']['nameday']['pl']
    names_string = names_string.replace(' ', '')
    names = names_string.split(',')
    return names
