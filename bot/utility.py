import datetime as dt
import hashlib
import re
from copy import deepcopy, copy

import discord
import pytz
from discord.ext import commands

from commands.weather import get_5_day_forecast


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


def split_embed(embed: discord.Embed, max_field_length: int = 1024) -> list[discord.Embed]:
    if len(str(embed.to_dict())) <= max_field_length:
        return [embed]

    # split embed dict into more dicts of given max length
    embeds = []
    current_embed = make_embed_dict_copy_without_fields(embed)
    for field in embed.fields:
        if len(str(current_embed)) + len(field.name) + len(field.value) <= max_field_length:
            current_embed['fields'].append({'name': field.name, 'value': field.value, 'inline': field.inline})
        elif len(str(field.value)) >= max_field_length:
            embeds.append(copy(current_embed))
            prefix = "..."
            postfix = "..."
            field_value_chunks = split_into_chunks(text=field.value,
                                                   max_char_length=max_field_length - len(prefix) - len(postfix))
            for i, chunk in enumerate(field_value_chunks):
                current_embed = make_embed_dict_copy_without_fields(embed)
                if i == 0:
                    new_field = {'name': field.name, 'value': chunk + postfix, 'inline': field.inline}
                elif i == len(field_value_chunks) - 1:
                    new_field = {'name': field.name, 'value': prefix + chunk, 'inline': field.inline}
                else:
                    new_field = {'name': field.name, 'value': prefix + chunk + postfix, 'inline': field.inline}
                current_embed['fields'].append(new_field)
                embeds.append(copy(current_embed))
                current_embed = make_embed_dict_copy_without_fields(embed)
        else:
            embeds.append(copy(current_embed))
            current_embed = make_embed_dict_copy_without_fields(embed)
            current_embed['fields'].append({'name': field.name, 'value': field.value, 'inline': field.inline})

    # back to embed class
    return [discord.Embed.from_dict(embed_dict) for embed_dict in embeds]


def make_embed_dict_copy_without_fields(embed: discord.Embed) -> dict:
    embed_copy = deepcopy(embed)
    embed_copy.clear_fields()
    return dict(embed_copy.to_dict())


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

    LOREM_IPSUM = (
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Ut interdum auctor metus id consequat. Duis rhoncus odio diam, sed fermentum dui lacinia in. Duis gravida quis tellus id faucibus. Nunc maximus ipsum a interdum eleifend. Vestibulum interdum egestas malesuada. Morbi posuere sem non consequat tempor. Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Sed posuere varius enim, posuere laoreet ligula convallis quis. Nullam vel ligula quis dolor ultrices ultrices eget id turpis. Mauris gravida sapien tempor, tristique dolor viverra, iaculis massa."

        "Proin eu erat vel velit tristique tincidunt. Sed id felis libero. Morbi consequat tincidunt finibus. Proin nec mi consectetur, ornare libero eu, dictum metus. Nunc imperdiet ac mauris eget porta. Phasellus nec egestas felis. Mauris pulvinar at mi id accumsan. Cras volutpat ligula magna, in placerat massa viverra vitae."

        "Sed rhoncus ligula ut ornare maximus. Praesent quis consectetur sapien, ac venenatis massa. Sed felis lectus, vehicula suscipit pulvinar porta, varius non erat. Quisque lobortis nec metus ut luctus. In et auctor nisi, sed sodales tellus. Suspendisse sodales mi sapien, ultricies iaculis metus malesuada quis. Vestibulum consectetur tempor purus. Proin consectetur suscipit dolor ac ornare. In hac habitasse platea dictumst. Praesent at porttitor metus, eget congue odio. Integer pulvinar elit quis augue fringilla dapibus."

        "Quisque consectetur feugiat maximus. Aenean gravida magna libero, non pulvinar nisi mollis et. Sed eget blandit risus. Aliquam ut consectetur nibh. Curabitur at sapien ut elit tempus fringilla. Quisque accumsan placerat nibh, et aliquet arcu viverra accumsan. Sed consectetur mi ut elit vehicula, suscipit dapibus ligula dictum. Fusce malesuada vestibulum tristique. In magna magna, maximus eget cursus ac, aliquam quis est. Duis luctus eros sit amet ante scelerisque, vel laoreet tortor pellentesque. Praesent eget porta metus. Aliquam vel felis ut magna facilisis fermentum a quis lacus."

        "Phasellus ligula libero, eleifend non metus id, convallis consequat nunc. Vestibulum suscipit justo ut imperdiet commodo. Integer ac sollicitudin nisl, id cursus nunc. Suspendisse fermentum rutrum augue id vestibulum. Proin molestie arcu eros. Aenean sed mi accumsan, commodo orci nec, lobortis sem. Donec nec eros ut turpis porttitor luctus. Vivamus in faucibus nibh. Donec ullamcorper molestie ex nec rhoncus. Suspendisse commodo sagittis arcu, in fringilla metus blandit ut. Ut auctor posuere nunc id scelerisque. Fusce gravida ex non commodo maximus. Etiam sit amet nunc vel dui rutrum pulvinar sit amet vitae dolor.")

    test_embed = discord.Embed(title="Test Embed", description="This is a test embed.")
    test_embed.add_field(name="Testr field", value="Test Value", inline=False)
    test_embed.add_field(name="Testr LONG field", value="Test LONG Value", inline=False)
    test_embed.add_field(name="Lorem", value=LOREM_IPSUM, inline=False)
    test_embeds = split_embed(test_embed)
    for embed in test_embeds:
        print(embed.title)
        print(embed.description)
        print(embed.fields)


if __name__ == '__main__':
    main()
