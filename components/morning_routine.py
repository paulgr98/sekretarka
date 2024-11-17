import asyncio
import datetime as dt
from typing import Optional

import discord

from commands import news
from components import (
    nameday as nd,
)
from components.fun_holidays import fun_holidays_api_v2 as fha
from config import config as cfg
from repositories.UserBirthDayByServerRepository import UserBirthDayByServerRepository

# Constants for better readability
MORNING_HOUR = 7
MORNING_MINUTE = 0
MORNING_SECOND = 0
SLEEP_INTERVAL_SECONDS = 10
NEWS_COUNT = 3

DAY_NAMES = {
    0: 'Poniedziałek',
    1: 'Wtorek',
    2: 'Środa',
    3: 'Czwartek',
    4: 'Piątek',
    5: 'Sobota',
    6: 'Niedziela'
}


async def morning_routine(bot_client: discord.Client, db_connector, show_news: bool):
    channels = await get_morning_channels(bot_client)
    now = dt.datetime.now()
    now_str = await get_today_date_str()

    welcome_text = "**Dzień dobry!**\n"
    welcome_text += f"Dzisiaj jest **{now_str}** - {DAY_NAMES[now.weekday()]}\n"

    names = nd.get_names()
    names = ', '.join(names)
    welcome_text += f"\n**Imieniny obchodzą:** {names}\n"

    channel_bday_info = {}
    for channel in channels:
        server_id: int = channel.guild.id
        bday_info = await get_birthday_text(bot_client, server_id, db_connector)
        channel_bday_info[channel.id] = ""
        if bday_info is not None:
            channel_bday_info[channel.id] = f"\n{bday_info}"

    holidays = await fun_holidays()
    holidays_text = f"\n{holidays}\n"

    if show_news:
        news_text = '\n**Aktualne wiadomości z TVN24:**'
        for channel in channels:
            welcome_text += channel_bday_info[channel.id]
            welcome_text += holidays_text
            welcome_text += news_text
            await channel.send(welcome_text)

        news_embeds = await news.get_news_embeds(NEWS_COUNT)
        for embed in news_embeds:
            for channel in channels:
                await channel.send(embed=embed)
    else:
        for channel in channels:
            welcome_text += channel_bday_info[channel.id]
            welcome_text += holidays_text
            await channel.send(welcome_text)


async def get_today_date_str():
    return dt.datetime.now().strftime('%d.%m.%Y')


async def fun_holidays():
    holidays = fha.FunHolidaysApi()
    names = holidays.get_holidays_for_today()
    if not names:
        return '**Dzisiaj nie obchodzimy żadnych świąt**\n'

    msg = '**Dzisiaj obchodzimy:**\n'
    for name in names:
        msg += f'- {name}\n'
    return msg


async def get_birthday_text(bot_client: discord.Client, server_id: int, db_connector) \
        -> Optional[str]:
    bdays: list = await get_server_bdays(server_id, db_connector)

    if bdays is None or not bdays:
        return None

    msg = '**Urodziny mają**\n'
    users = []

    for user_id, date in bdays:
        user = discord.utils.get(bot_client.get_all_members(), id=int(user_id))
        if user:
            users.append(user)
            date_dt = dt.datetime.strptime(date, '%d.%m.%Y')
            age = dt.datetime.now().year - date_dt.year
            msg += f'- {user.display_name} ({age} lat)\n'

    if users:
        msg += '\n'
        msg += ' '.join([usr.mention for usr in users])
        msg += '\n**Wszystkiego najlepszego!** Zdrówka i spełnienia marzeń :heart:\n'

    return msg


async def get_server_bdays(server_id: int, db_connector) -> list[tuple]:
    bday_repo = UserBirthDayByServerRepository(db_connector)
    now_str = await get_today_date_str()
    bdays = bday_repo.get_birthday_for_date(server_id, now_str)
    return bdays


async def get_morning_channels(bot_client: discord.Client):
    channels = [bot_client.get_channel(channel_id) for channel_id in cfg.MORNING_CHANNEL_ID]
    return channels


async def schedule_morning_routine(bot_client: discord.Client, db_connector, show_news: bool = True):
    while True:
        now = dt.datetime.now()

        # Determine target time
        if now.hour >= MORNING_HOUR and now.minute >= MORNING_MINUTE:
            target = (now + dt.timedelta(days=1)).replace(
                hour=MORNING_HOUR, minute=MORNING_MINUTE, second=MORNING_SECOND, microsecond=0
            )
        else:
            target = now.replace(
                hour=MORNING_HOUR, minute=MORNING_MINUTE, second=MORNING_SECOND, microsecond=0
            )

        # Calculate wait time in seconds
        wait_time = (target - now).total_seconds()

        # Wait until the target time
        await asyncio.sleep(wait_time)

        # Execute the morning routine
        await morning_routine(bot_client, db_connector, show_news)

        # Wait a bit before starting the loop again to prevent immediate re-execution in edge cases
        await asyncio.sleep(SLEEP_INTERVAL_SECONDS)
