import re

import discord
from discord.ext import commands


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


def has_role(role_name: str, member: discord.Member) -> bool:
    return role_name in [role.name for role in member.roles]


def has_roles(role_names: list[str], member: discord.Member) -> bool:
    return any(role_name in [role.name for role in member.roles] for role_name in role_names)


def split_into_chunks(text: str, max_char_length: int) -> list[str]:
    """
    Splits text by whitespace into chunks of max_char_length characters
    """
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
