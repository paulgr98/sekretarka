import discord
from discord.ext import commands


async def get_user_from_mention(ctx: commands.Context, mention: str):
    try:
        # <@!user_id> -> user_id
        user_id = str(mention)[2:-1]
        # get user object from id
        member = discord.utils.get(ctx.guild.members, id=int(user_id))
        return member
    except ValueError:
        return None
