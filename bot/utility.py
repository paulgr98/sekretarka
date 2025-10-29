import datetime as dt
import hashlib
import re

import discord
import pytz
import tzdata
from discord.ext import commands

from weather import get_5_day_forecast


async def get_user_from_mention(ctx: commands.Context, mention: str) -> discord.Member or None:
    try:
        # <@!user_id> -> user_id
        user_id = str(mention)[2:-1]
        # get user object from id
        member = discord.utils.get(ctx.guild.members, id=int(user_id))
        return member
    except ValueError:
        return None


async def get_user_from_username(ctx: commands.Context, username: str) -> discord.Member or None:
    try:
        # get user object from username
        member = discord.utils.get(ctx.guild.members, name=username)
        return member
    except ValueError:
        return None


async def get_user_from_id(ctx: commands.Context, user_id: int) -> discord.Member or None:
    try:
        # Fetch user object from id
        user = await ctx.bot.fetch_user(user_id)
        return user
    except discord.NotFound:
        return None
    except discord.HTTPException:
        return None


def has_role(role_name: str, member: discord.Member) -> bool:
    return role_name in [role.name for role in member.roles]


def has_roles(role_names: list[str], member: discord.Member) -> bool:
    return any(role_name in [role.name for role in member.roles] for role_name in role_names)


def split_into_chunks(text: str, max_char_length: int) -> list[str]:
    chunks = []
    current_chunk = ""
    words = re.split(r'(\s)', text)  # split by whitespace and keep it
    for word in words:
        if len(current_chunk) + len(word) <= max_char_length:
            current_chunk += word
        else:
            chunks.append(current_chunk)
            current_chunk = word
    chunks.append(current_chunk)
    return chunks


async def add_role_for_user(ctx: commands.Context, role_name: str):
    role = discord.utils.get(ctx.guild.roles, name=role_name)
    if role is None:
        role = await add_role_to_server(ctx, role_name)
    if await does_user_have_role(ctx, role_name):
        await ctx.reply(f'Posiadasz już rolę {role_name}')
        return False
    await ctx.author.add_roles(role)
    return True


async def does_user_have_role(ctx: commands.Context, role_name: str):
    role = discord.utils.get(ctx.guild.roles, name=role_name)
    if role is None:
        return False
    return role in ctx.author.roles


async def add_role_to_server(ctx: commands.Context, role_name: str):
    role = await ctx.guild.create_role(
        name=role_name,
        color=discord.Color.light_gray(),
        hoist=False,
        mentionable=False,
    )
    return role


async def remove_role_from_user(ctx: commands.Context, role_name: str):
    role = discord.utils.get(ctx.guild.roles, name=role_name)
    # check if the user has the role
    if not does_user_have_role(ctx, role_name):
        await ctx.reply(f'Nie posiadasz roli {role_name}')
        return False
    await ctx.author.remove_roles(role)
    return True


async def try_remove_role_from_server(ctx: commands.Context, role_name: str):
    # if no user has the role, remove it from the server
    role = discord.utils.get(ctx.guild.roles, name=role_name)
    if role is None:
        return
    if len(role.members) == 0:
        await role.delete()


def generate_objects_hash(*objects_ids, include_date: bool = False, date: dt.datetime = None) -> str:
    if include_date and date is None:
        date = dt.datetime.now()
    hash_key = hashlib.sha1()
    for obj_id in objects_ids:
        hash_key.update(str(obj_id).encode('utf-8'))
    if include_date:
        date_str = date.strftime('%d.%m.%Y')
        hash_key.update(str(date_str).encode('utf-8'))
    return hash_key.hexdigest()

def str_to_utc_datetime(dt_str: str) -> dt.datetime:
    utc_timezone = pytz.timezone('UTC')
    dt_obj = dt.datetime.strptime(dt_str, '%Y-%m-%dT%H:%M')
    dt_obj = utc_timezone.localize(dt_obj)
    return dt_obj

def cast_to_local_datetime(dt_obj: dt.datetime) -> dt.datetime:
    local_timezone = pytz.timezone('Europe/Warsaw')
    dt_obj = dt_obj.astimezone(local_timezone)
    return dt_obj

def get_tomorrow_sunrise() -> str:
    wthr_json = get_5_day_forecast("Warsaw")
    sunrise_iso = wthr_json["daily"]["sunrise"][1]
    dt_obj = str_to_utc_datetime(sunrise_iso)
    sunrise_local = cast_to_local_datetime(dt_obj).strftime('%H:%M')
    return sunrise_local


def main():
    print(get_tomorrow_sunrise())
    hash1 = generate_objects_hash('123', include_date=False)
    print(hash1)
    hash2 = generate_objects_hash('123', include_date=True)
    print(hash2)
    hash3 = generate_objects_hash('123', '456', include_date=False)
    print(hash3)
    hash4 = generate_objects_hash('123', '456', include_date=True)
    print(hash4)


if __name__ == '__main__':
    main()
