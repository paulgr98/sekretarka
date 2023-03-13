from formula1py import F1
import datetime as dt
import pytz
import json
import asyncio
import discord
import config as cfg
from typing import Coroutine, Callable


# dict_keys(['season', 'round', 'url', 'raceName', 'Circuit', 'date', 'time', 'FirstPractice', 'SecondPractice',
# 'ThirdPractice', 'Qualifying'])

# dict_keys(['season', 'round', 'url', 'raceName', 'Circuit', 'date', 'time', 'FirstPractice', 'Qualifying',
# 'SecondPractice', 'Sprint'])

def get_current_season():
    f1 = F1()
    # Get the current season
    current_season = f1.current_schedule().json['MRData']['RaceTable']
    return current_season


def get_next_race(target_dt: dt.datetime):
    season = get_current_season()
    races_list = season['Races']

    # convert target_dt to local timezone
    target_dt = dt_to_local_dt(target_dt)

    next_race = None
    for race in races_list:
        race_date = race['date']
        race_time = race['time']
        local_race_dt = str_to_local_dt(race_date, race_time)
        # skipping all the races that are in the past
        # get first race that is in the future
        if local_race_dt > target_dt:
            next_race = race
            break
    return next_race


async def schedule_f1_notifications(client: discord.Client):
    await scheduler(client, get_race_time, race_notification)


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


async def scheduler(client: discord.Client,
                    get_target_dt: Callable[[], dt.datetime],
                    take_action: Callable[[discord.Client], Coroutine]) -> None:
    while True:
        # 15 minutes before race
        target_dt = get_target_dt()
        target_dt -= dt.timedelta(minutes=15)
        now = get_now_time()
        wait_time = (target_dt - now).total_seconds()
        # if time already passed, skip this iteration
        if wait_time < 0:
            continue
        # wait until the target time
        await asyncio.sleep(wait_time)
        now = get_now_time()
        # check if the target time has been reached
        if now.day == target_dt.day and now.hour == target_dt.hour and now.minute == target_dt.minute:
            await take_action(client)
            # wait for 4 days until the race week ends
            four_days_time = dt.timedelta(days=4).total_seconds()
            await asyncio.sleep(four_days_time)


async def race_notification(client: discord.Client) -> None:
    channel = client.get_channel(cfg.MORNING_CHANNEL_ID)
    # get f1_notify role
    role = discord.utils.get(channel.guild.roles, name='f1_notify')

    # send notification
    await channel.send(f'{role.mention} Wyścig zaczyna się za 15 minut!')


if __name__ == '__main__':
    current_dt = dt.datetime.now()
    nearest_race = get_next_race(current_dt)
    print(json.dumps(nearest_race, indent=4))
