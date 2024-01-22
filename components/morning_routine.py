import asyncio
import calendar
import datetime as dt

import discord

import config as cfg
from commands import (
    news,
    birthday_tracker as bt,
)
from components import (
    nameday as nd,
)
from components.fun_holidays import fun_holidays_api_v2 as fha


async def morning_routine(client: discord.Client, show_news: bool):
    channels = [client.get_channel(cid) for cid in cfg.MORNING_CHANNEL_ID]

    day_names = {0: 'Poniedziałek', 1: 'Wtorek', 2: 'Środa', 3: 'Czwartek', 4: 'Piątek', 5: 'Sobota', 6: 'Niedziela'}
    now = dt.datetime.now()

    welcome_text = "**Dzień dobry!**\n"
    welcome_text += f"Dzisiaj jest **{now.strftime('%d.%m.%Y')}** - {day_names[now.weekday()]}\n"

    names = nd.get_names()
    names = ', '.join(names)
    welcome_text += f"\n**Imieniny obchodzą:** {names}\n"

    bday_info = await get_birthday_text(client)
    if bday_info is not None:
        welcome_text += '\n'
        welcome_text += bday_info

    holidays = await fun_holidays()
    welcome_text += f"\n{holidays}\n"

    if show_news:
        welcome_text += '\n**Aktualne wiadomości z TVN24:**'
        for channel in channels:
            await channel.send(welcome_text)

        news_embeds = news.get_news_embeds(3)
        for embed in news_embeds:
            for channel in channels:
                await channel.send(embed=embed)
    else:
        for channel in channels:
            await channel.send(welcome_text)


async def fun_holidays():
    holidays = fha.FunHolidaysApi()
    names = holidays.get_holidays_for_today()
    msg = ''
    if len(names) == 0 or names is None:
        msg = '**Dzisiaj nie obchodzimy żadnych nietypowych świąt**\n'
    else:
        '**Dzisiaj obchodzimy:**\n'
        for name in names:
            msg += f'- {name}\n'
    return msg


async def get_birthday_text(client: discord.Client):
    bdays = await bt.get_today_birthdays()
    if bdays is None:
        return None
    msg = '**Urodziny mają**\n'
    users = []
    for user_id, date in bdays:
        user = discord.utils.get(client.get_all_members(), id=int(user_id))
        users.append(user)
        date_dt = dt.datetime.strptime(date, '%d.%m.%Y')
        age = dt.datetime.now().year - date_dt.year
        msg += f'- {user.display_name} ({age} lat)\n'

    msg += '\n'
    for usr in users:
        msg += f'{usr.mention} '
    msg += '\n**Wszystkiego najlepszego!** Zdrówka i spełnienia marzeń :heart:\n'

    return msg


async def schedule_morning_routine(client: discord.Client, show_news: bool = True):
    # set target time to 7:00
    target = dt.datetime.now()
    target = target.replace(hour=7, minute=0, second=0, microsecond=0)
    awaited_today = False
    while True:
        now = dt.datetime.now()
        wait_time = (target - now).total_seconds()
        if wait_time < 0:
            # if the target time has already passed, set target time to 7:00 tomorrow
            target += dt.timedelta(days=1)
            continue
        # wait for the amount of time left until the target time
        await asyncio.sleep(wait_time)
        awaited_today = False
        now = dt.datetime.now()
        if now.day == target.day and now.hour == target.hour and now.minute == target.minute and not awaited_today:
            target += dt.timedelta(days=1)
            awaited_today = True
            # execute morning routine and set target time to 7:00 tomorrow
            await morning_routine(client, show_news)
