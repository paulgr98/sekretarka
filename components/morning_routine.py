import asyncio
import datetime as dt
from typing import Optional

import discord
from discord.ext import commands

from bot.database.DbConnector import DbConnector
from bot.logger import logger
from components import nameday as nd
from components.fun_holidays import fun_holidays_api_v2 as fha
from repositories.MorningChannelsByServerRepository import MorningChannelsByServerRepository
from repositories.UserBirthDayByServerRepository import UserBirthDayByServerRepository

MORNING_HOUR, MORNING_MINUTE, MORNING_SECOND = 7, 0, 0
SLEEP_INTERVAL_SECONDS = 10
DAY_NAMES = ['Poniedziałek', 'Wtorek', 'Środa', 'Czwartek', 'Piątek', 'Sobota', 'Niedziela']


async def add_channel_to_morning_routine(db_connector: DbConnector, channel: discord.TextChannel):
    """Add a channel to the morning routine."""
    repo = MorningChannelsByServerRepository(db_connector)
    try:
        await repo.add_channel(channel.guild.id, channel.id)
    except Exception as e:
        # Log the exception if needed (e.g., logging library or print statement)
        logger.error(f"Error adding channel {channel.id}: {e}")
        return False
    return True


async def remove_channel_from_morning_routine(db_connector: DbConnector, channel: discord.TextChannel):
    """Remove a channel from the morning routine."""
    repo = MorningChannelsByServerRepository(db_connector)
    try:
        await repo.remove_channel(channel.guild.id, channel.id)
    except Exception as e:
        # Log the exception if needed (e.g., logging library or print statement)
        logger.error(f"Error removing channel {channel.id}: {e}")
        return False
    return True


async def get_today_date_str() -> str:
    """Get the current date as a formatted string."""
    return dt.datetime.now().strftime('%d.%m.%Y')


async def fetch_fun_holidays() -> str:
    """Fetch today's fun holidays."""
    holidays = fha.FunHolidaysApi()
    names = holidays.get_holidays_for_today()
    if not names:
        return '**Dzisiaj nie obchodzimy żadnych świąt**\n'
    return '**Dzisiaj obchodzimy:**\n' + ''.join(f'- {name}\n' for name in names)


async def get_birthday_text(guild: discord.Guild, db_connector: DbConnector) -> Optional[str]:
    """Fetch today's birthdays for a specific server."""
    bday_repo = UserBirthDayByServerRepository(db_connector)
    today_str = await get_today_date_str()
    bdays = await bday_repo.get_birthday_for_date(guild.id, today_str)

    if not bdays:
        return None

    msg = '**Urodziny mają**\n'
    users = [discord.utils.get(guild.members, id=int(uid)) for uid, _ in bdays]
    users = [user for user in users if user]

    for user, (_, date) in zip(users, bdays):
        age = dt.datetime.now().year - dt.datetime.strptime(date, '%d.%m.%Y').year
        msg += f'- {user.display_name} ({age} lat)\n'

    if users:
        mentions = ' '.join(user.mention for user in users)
        msg += f'\n{mentions}\n**Wszystkiego najlepszego!** Zdrówka i spełnienia marzeń :heart:\n'
    return msg


async def get_morning_channels(bot_client: discord.Client, db_connector: DbConnector, server_id: int) -> list[
    discord.TextChannel]:
    """Retrieve the list of channels for morning messages."""
    repo = MorningChannelsByServerRepository(db_connector)
    channels_ids = await repo.get_channels(server_id)
    return [bot_client.get_channel(int(cid)) for cid in channels_ids if bot_client.get_channel(int(cid))]


async def send_morning_message(channels: list[discord.TextChannel], message: str):
    """Send the morning message to all specified channels."""
    for channel in channels:
        if channel:
            await channel.send(message)


async def generate_morning_message(guild: discord.Guild, db_connector: DbConnector) -> str:
    """Generate the full morning message for a specific server."""
    now_str = await get_today_date_str()
    welcome_text = f"**Dzień dobry!**\nDzisiaj jest **{now_str}** - {DAY_NAMES[dt.datetime.now().weekday()]}\n"
    namedays = nd.get_names()
    namedays = ', '.join(namedays) if namedays else 'nie mam pojęcia kto dzisiaj obchodzi imieniny, coś się zepsuło.'
    bday_text = await get_birthday_text(guild, db_connector)
    holidays_text = await fetch_fun_holidays()

    message = f"{welcome_text}\n**Imieniny obchodzą:** {namedays}\n\n"
    if bday_text:
        message += bday_text
    message += holidays_text
    return message


async def morning_routine_all(bot_client: discord.Client, db_connector: DbConnector):
    """Send the morning message to all servers configured."""
    for guild in bot_client.guilds:
        channels = await get_morning_channels(bot_client, db_connector, guild.id)
        if channels:
            message = await generate_morning_message(guild, db_connector)
            await send_morning_message(channels, message)


async def morning_routine_single(ctx: commands.Context, db_connector: DbConnector):
    """Send the morning message to a specific server initiated by a user command."""
    channels = await get_morning_channels(ctx.bot, db_connector, ctx.guild.id)
    if not channels:
        await ctx.reply(f"Brak dodanych kanałów.\nUżyj komendy {ctx.bot.command_prefix}morning add <#kanal_tekstowy>")
        return
    message = await generate_morning_message(ctx.guild, db_connector)
    await send_morning_message(channels, message)


async def schedule_morning_routine(bot_client: discord.Client, db_connector: DbConnector):
    """Schedule the morning routine every day at the specified time."""
    while True:
        now = dt.datetime.now()
        if now.hour >= MORNING_HOUR and now.minute >= MORNING_MINUTE:
            target = (now + dt.timedelta(days=1)).replace(
                hour=MORNING_HOUR, minute=MORNING_MINUTE, second=MORNING_SECOND, microsecond=0
            )
        else:
            target = now.replace(
                hour=MORNING_HOUR, minute=MORNING_MINUTE, second=MORNING_SECOND, microsecond=0
            )
        wait_time = (target - now).total_seconds()
        await asyncio.sleep(wait_time)
        await morning_routine_all(bot_client, db_connector)
