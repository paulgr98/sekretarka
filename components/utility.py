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


def has_role(role_name: str, member: discord.Member) -> bool:
    return role_name in [role.name for role in member.roles]
