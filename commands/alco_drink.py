import discord

from components import cocktails_db_wrapper as cdb


def make_drink_embed(drink_name: str) -> (discord.Embed, None):
    # if no drink_json name is given, get a random drink_json
    cocktails_db = cdb.CocktailsDB()
    if drink_name is None:
        drink_json = cocktails_db.get_random_drink()
    else:
        drink_json = cocktails_db.get_drink_by_name(drink_name)

    if drink_json is None or drink_json['drinks'] is None:
        return None

    name = drink_json['drinks'][0]['strDrink']
    category = drink_json['drinks'][0]['strCategory']
    glass = drink_json['drinks'][0]['strGlass']
    instructions = drink_json['drinks'][0]['strInstructions']

    # insert new line after dot or comma in instructions if it's too long
    image_url = drink_json['drinks'][0]['strDrinkThumb']

    ingredients_and_measurements = []
    for i in range(1, 15):
        if drink_json['drinks'][0]['strIngredient' + str(i)]:
            if drink_json['drinks'][0]['strMeasure' + str(i)]:
                ingredients_and_measurements.append(
                    f"-> {drink_json['drinks'][0]['strIngredient' + str(i)]} "
                    f"({str(drink_json['drinks'][0]['strMeasure' + str(i)]).strip()})"
                )
            else:
                ingredients_and_measurements.append(
                    f"-> {drink_json['drinks'][0]['strIngredient' + str(i)]}"
                )

    ingredients_str = '\n'.join(ingredients_and_measurements)
    ingredients_str = ingredients_str.strip()

    embed = discord.Embed(title=name, color=0x571E1E)
    embed.set_thumbnail(url=image_url)
    embed.add_field(name='Kategoria', value=category, inline=False)
    embed.add_field(name='Szkło', value=glass, inline=False)
    embed.add_field(name='Składniki', value=ingredients_str, inline=False)
    embed.add_field(name='Instrukcja', value=instructions, inline=False)

    return embed
