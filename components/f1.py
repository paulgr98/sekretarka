import asyncio
import datetime as dt
import json
from typing import Coroutine, Callable

import discord
import pytz

from bot.database.DbConnector import DbConnector
from bot.logger import logger
from components.f1_api import F1
from repositories.F1ChannelsByServerRepository import F1ChannelsByServerRepository


def get_current_season():
    f1 = F1()
    current_season = f1.current_schedule().json['MRData']['RaceTable']
    return current_season


def get_next_race(target_dt: dt.datetime):
    season = get_current_season()
    races_list = season['Races']

    target_dt = dt_to_local_dt(target_dt)

    next_race = None
    for race in races_list:
        race_date = race['date']
        race_time = race['time']
        local_race_dt = str_to_local_dt(race_date, race_time)
        if local_race_dt > target_dt:
            next_race = race
            break
    return next_race


async def schedule_f1_notifications(client: discord.Client, db_connector: DbConnector):
    now = get_now_time()
    race = get_next_race(now)

    if race is None:
        return

    tasks = [
        scheduler(client, db_connector, get_qualification_time, qualifying_notification),
        scheduler(client, db_connector, get_race_time, race_notification)
    ]

    if "SprintQualifying" in race:
        tasks.append(scheduler(client, get_sprint_qualifying_time, sprint_qualifying_notification))

    if "Sprint" in race:
        tasks.append(scheduler(client, get_sprint_time, sprint_notification))

    await asyncio.gather(*tasks)


def get_now_time() -> dt.datetime:
    local_timezone = pytz.timezone('Europe/Warsaw')
    now = dt.datetime.now()
    now = local_timezone.localize(now)
    return now


def get_race_time() -> dt.datetime:
    now = get_now_time()
    race = get_next_race(now)

    race_date = race['date']
    race_time = race['time']
    race_target = str_to_local_dt(race_date, race_time)
    return race_target


def get_qualification_time() -> dt.datetime:
    now = get_now_time()
    race = get_next_race(now)

    quali_date = race['Qualifying']['date']
    quali_time = race['Qualifying']['time']
    quali_target = str_to_local_dt(quali_date, quali_time)
    return quali_target


def get_sprint_time() -> dt.datetime:
    now = get_now_time()
    race = get_next_race(now)

    sprint_date = race['Sprint']['date']
    sprint_time = race['Sprint']['time']
    sprint_target = str_to_local_dt(sprint_date, sprint_time)
    return sprint_target


def get_sprint_qualifying_time() -> dt.datetime:
    now = get_now_time()
    sq = get_next_race(now)

    sq_date = sq['SprintQualifying']['date']
    sq_time = sq['SprintQualifying']['time']
    sq_target = str_to_local_dt(sq_date, sq_time)
    return sq_target


def str_to_local_dt(date: str, time: str) -> dt.datetime:
    utc_timezone = pytz.timezone('UTC')

    dt_str = f'{date}T{time}'
    dt_obj = dt.datetime.strptime(dt_str, '%Y-%m-%dT%H:%M:%SZ')
    dt_obj = utc_timezone.localize(dt_obj)
    dt_obj = dt_to_local_dt(dt_obj)
    return dt_obj


def dt_to_local_dt(dt_obj: dt.datetime) -> dt.datetime:
    local_timezone = pytz.timezone('Europe/Warsaw')
    dt_obj = dt_obj.astimezone(local_timezone)
    return dt_obj


def timedelta_to_str(dt_obj: dt.timedelta) -> str:
    days = dt_obj.days
    hours = dt_obj.seconds // 3600
    minutes = (dt_obj.seconds // 60) % 60

    res_str = ''

    if days > 0:
        res_str += f'{days} dn. '
    if hours > 0:
        res_str += f'{hours} godz. '
    res_str += f'{minutes} min.'

    return res_str


async def scheduler(client: discord.Client,
                    db_connector: DbConnector,
                    get_target_dt: Callable[[], dt.datetime],
                    take_action: Callable[[discord.Client, DbConnector], Coroutine]) -> None:
    while True:
        target_dt = get_target_dt()
        target_dt -= dt.timedelta(minutes=15)
        now = get_now_time()
        wait_time = (target_dt - now).total_seconds()
        if wait_time < 0:
            break
        await asyncio.sleep(wait_time)
        now = get_now_time()
        if now.day == target_dt.day and now.hour == target_dt.hour and now.minute == target_dt.minute:
            await take_action(client, db_connector)
            wait_until_next_race_week = dt.timedelta(days=4).total_seconds()
            await asyncio.sleep(wait_until_next_race_week)


async def race_notification(client: discord.Client) -> None:
    await send_notification_all(client, 'Wyścig zaczyna się za 15 minut!')


async def qualifying_notification(client: discord.Client) -> None:
    await send_notification_all(client, 'Kwalifikacje zaczynają się za 15 minut!')


async def sprint_notification(client: discord.Client) -> None:
    await send_notification_all(client, 'Sprint zaczyna się za 15 minut!')


async def sprint_qualifying_notification(client: discord.Client) -> None:
    await send_notification_all(client, 'Kwalifikacje sprintu zaczynają się za 15 minut!')


async def add_f1_channel(db_connector: DbConnector, channel: discord.TextChannel) -> bool:
    repo = F1ChannelsByServerRepository(db_connector)
    try:
        await repo.add_channel(channel.guild.id, channel.id)
    except Exception as e:
        logger.error(f"Error adding channel {channel.id}: {e}")
        return False
    return True


async def remove_f1_channel(db_connector: DbConnector, channel: discord.TextChannel) -> bool:
    repo = F1ChannelsByServerRepository(db_connector)
    try:
        await repo.remove_channel(channel.guild.id, channel.id)
    except Exception as e:
        logger.error(f"Error removing channel {channel.id}: {e}")
        return False
    return True


async def get_f1_channels(bot_client: discord.Client, db_connector: DbConnector, server_id: int) -> list[
    discord.TextChannel]:
    repo = F1ChannelsByServerRepository(db_connector)
    channels_ids = await repo.get_channels(server_id)
    # remove potential duplicates just in case, IDK
    unique_ids = list(dict.fromkeys(int(cid) for cid in channels_ids))
    channels = [bot_client.get_channel(cid) for cid in unique_ids]
    return [ch for ch in channels if ch]


async def send_notification_all(client: discord.Client, message: str, db_connector: DbConnector):
    for guild in client.guilds:
        channels = await get_f1_channels(client, db_connector, guild.id)
        if channels:
            await notify(channels, message)


async def notify(channels, message: str) -> None:
    for channel in channels:
        if channel:
            role = discord.utils.get(channel.guild.roles, name='f1_notify')
            await channel.send(f'{role.mention} {message}')


if __name__ == '__main__':
    current_dt = dt.datetime.now()
    nearest_race = get_next_race(current_dt)
    print(json.dumps(nearest_race, indent=4))
