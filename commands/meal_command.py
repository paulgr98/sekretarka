import asyncio
import random
from typing import Optional

import discord
from discord.ext import commands

from components.meal_db_wrapper import MealDB


async def get_ingredients_and_measurements(meal_dict) -> list:
    ingredients_and_measurements = []
    for i in range(1, 50):
        ingredient_key = 'strIngredient' + str(i)
        if ingredient_key in meal_dict and meal_dict[ingredient_key]:
            measurement_key = 'strMeasure' + str(i)
            if measurement_key in meal_dict and meal_dict[measurement_key]:
                ingredients_and_measurements.append(
                    f"{meal_dict[ingredient_key]} ({str(meal_dict[measurement_key]).strip()})")
            else:
                ingredients_and_measurements.append(
                    f"{meal_dict[ingredient_key]}")
    return ingredients_and_measurements


async def make_meal_embed(meal_dict):
    discord_embed_field_limit = 1024
    if meal_dict is None:
        return None
    name = meal_dict['strMeal']
    embed = discord.Embed(title=name, color=0x571E1E)
    embed.set_thumbnail(url=meal_dict['strMealThumb'])
    embed.add_field(name='Kategoria', value=meal_dict['strCategory'], inline=False)
    embed.add_field(name='Region', value=meal_dict['strArea'], inline=False)

    ingredients_and_measurements = await get_ingredients_and_measurements(meal_dict)
    ingredients_str = ', '.join(ingredients_and_measurements)
    ingredients_str = ingredients_str.strip()
    embed.add_field(name='Składniki', value=ingredients_str, inline=False)

    instructions = meal_dict['strInstructions']
    if len(instructions) > discord_embed_field_limit:
        instructions = instructions[:discord_embed_field_limit - 3] + '...'

    embed.add_field(name='Instrukcja', value=instructions, inline=False)
    return embed


async def process_args(*args):
    options_values = {}
    for arg in args:
        if arg.startswith('--'):
            option = arg[2:]
            try:
                options_values[option] = args[args.index(arg) + 1]
            except IndexError:
                options_values[option] = None

    return options_values


def get_options():
    usage_str = """
    Uzycie:
        meal [opcje] [argumenty]
        np: meal --category śniadanie
        lub: meal --category obiad --region Włochy\n
    """
    options_str = """
    Opcje:
        --name: wyszukuje posiłek po nazwie
        --random: wyszukuje całkowicie losowy przepis
        --list: lista dostępnych kategorii i regionów
        --category: kategoria (np. śniadanie, obiad, wegańskie)
        --area: region kuchni (np. kuchnia Włoska, Polska)
        --ingredient: składnik (np. kurczak, ziemniaki)
    """
    return usage_str + options_str


def calc_common_meals(meals: list[list[dict]]) -> list[dict]:
    sets = [set(tuple(d.items()) for d in meal) for meal in meals]
    common = set.intersection(*sets)
    result = [dict(t) for t in common]
    return result


class MealCommand:
    def __init__(self, ctx: commands.Context = None):
        self.ctx = ctx
        self.api = MealDB()

    async def get_embed(self, *args) -> Optional[discord.Embed]:
        options = await process_args(*args)
        if options is None:
            return None
        meal = await self.get_meal(options)
        embed = await make_meal_embed(meal)
        return embed

    async def get_meal(self, options: dict[str, str]):
        meal = None
        if "random" in options.keys():
            return self.api.get_random_meal()

        if "name" in options.keys():
            return self.api.get_meal_by_name(options["name"])

        meals = await self.filter_meals(options)
        if len(meals) > 0:
            meal_id = random.choice(meals)['idMeal']
            meal = self.api.get_meal_by_id(meal_id)

        return meal

    async def filter_meals(self, options: dict[str, str]):
        meals: list[list] = []
        if "category" in options.keys():
            meals.append(self.api.filter_by_category(options["category"]))
        if "area" in options.keys():
            meals.append(self.api.filter_by_area(options["area"]))
        if "ingredient" in options.keys():
            meals.append(self.api.filter_by_ingredient(options["ingredient"]))
        if len(meals) == 0:
            return []
        meals = [meal_list or [] for meal_list in meals]
        if len(meals) == 1:
            return meals[0]
        result = calc_common_meals(meals)
        return result

    async def list_filter_options(self):
        categories = self.api.list_categories()
        areas = self.api.list_areas()
        list_str = f"**Kategorie**:\n{', '.join(categories)}\n\n**Regiony**:\n{', '.join(areas)}"
        return list_str


async def main():
    options = ["--category", "obiad", "--area"]
    print(await process_args(*options))


if __name__ == "__main__":
    asyncio.run(main())
