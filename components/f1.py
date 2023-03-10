from formula1py import F1
import datetime as dt
import pytz
import json
import asyncio
import discord
import config as cfg


def get_current_season():
    f1 = F1()
    # Get the current season
    current_season = f1.current_schedule().json['MRData']['RaceTable']
    return current_season


def get_next_race(target_dt: dt.datetime):
    season = get_current_season()
    races_list = season['Races']

    # dict_keys(['season', 'round', 'url', 'raceName', 'Circuit', 'date', 'time', 'FirstPractice', 'SecondPractice',
    # 'ThirdPractice', 'Qualifying'])

    # dict_keys(['season', 'round', 'url', 'raceName', 'Circuit', 'date', 'time', 'FirstPractice', 'Qualifying',
    # 'SecondPractice', 'Sprint'])

    # convert target_dt to local timezone
    local_timezone = pytz.timezone('Europe/Warsaw')
    target_dt = target_dt.astimezone(local_timezone)

    next_race = None
    for race in races_list:
        race_date = race['date']
        race_time = race['time']
        # race time is in UTC
        dt_str = f'{race_date}T{race_time}'
        race_dt = dt.datetime.strptime(dt_str, '%Y-%m-%dT%H:%M:%SZ')
        # convert race time to local timezone
        local_race_dt = race_dt.astimezone(local_timezone)
        # skipping all the races that are in the past
        # get first race that is in the future
        if local_race_dt > target_dt:
            next_race = race
            break
    return next_race


async def schedule_f1_notifications(client: discord.Client):
    local_timezone = pytz.timezone('Europe/Warsaw')
    while True:
        race = get_next_race(dt.datetime.now())
        race_date = race['date']
        race_time = race['time']
        race_dt_str = f'{race_date}T{race_time}'
        race_dt = dt.datetime.strptime(race_dt_str, '%Y-%m-%dT%H:%M:%SZ')
        target = race_dt.astimezone(local_timezone)

        # 15 minutes before race
        target -= dt.timedelta(minutes=15)
        now = dt.datetime.now()
        now = now.astimezone(local_timezone)
        wait_time = (target - now).total_seconds()
        if wait_time < 0:
            continue
        await asyncio.sleep(wait_time)
        now = dt.datetime.now()
        now = now.astimezone(local_timezone)
        if now.day == target.day and now.hour == target.hour and now.minute == target.minute:
            await f1_notification(client)
            one_day_time = 60 * 60 * 24
            await asyncio.sleep(one_day_time)


async def f1_notification(client: discord.Client):
    channel = client.get_channel(cfg.MORNING_CHANNEL_ID)
    # get f1_notify role
    role = discord.utils.get(channel.guild.roles, name='f1_notify')

    # send notification
    await channel.send(f'{role.mention} Wyścig zaczyna się za 15 minut!')


if __name__ == '__main__':
    current_dt = dt.datetime.now()
    nearest_race = get_next_race(current_dt)
    print(json.dumps(nearest_race, indent=4))
