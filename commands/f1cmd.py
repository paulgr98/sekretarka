from components import f1
import datetime as dt
import pytz
import discord


def make_next_race_embed():
    current_dt = dt.datetime.now()
    race = f1.get_next_race(current_dt)

    # dict_keys(['season', 'round', 'url', 'raceName', 'Circuit', 'date', 'time', 'FirstPractice', 'Qualifying',
    # 'SecondPractice', 'Sprint'])
    race_round = race['round']
    race_name = race['raceName']
    embed = discord.Embed(
        title=f'#{race_round} {race_name}',
        colour=0xff2800
    )
    embed.add_field(name="Tor:", value=race['Circuit']['circuitName'], inline=False)

    local_timezone = pytz.timezone('Europe/Warsaw')

    day_names = {0: 'Poniedziałek', 1: 'Wtorek', 2: 'Środa', 3: 'Czwartek', 4: 'Piątek', 5: 'Sobota', 6: 'Niedziela'}

    quali_date = race['Qualifying']['date']
    quali_time = race['Qualifying']['time']
    quali_dt_str = f'{quali_date}T{quali_time}'
    quali_dt = dt.datetime.strptime(quali_dt_str, '%Y-%m-%dT%H:%M:%SZ')
    quali_dt_local = quali_dt.astimezone(local_timezone)
    quali_date = quali_dt_local.date().strftime('%d.%m.%Y')
    quali_time = quali_dt_local.time().strftime('%H:%M')
    quali_day = quali_dt_local.weekday()
    quali_day = day_names[quali_day]
    embed.add_field(name="Kwalifikacje:", value=f'{quali_date} ({quali_day}) godz. {quali_time}', inline=False)

    if 'Sprint' in race:
        sprint_date = race['Sprint']['date']
        sprint_time = race['Sprint']['time']
        sprint_dt_str = f'{sprint_date}T{sprint_time}'
        sprint_dt = dt.datetime.strptime(sprint_dt_str, '%Y-%m-%dT%H:%M:%SZ')
        sprint_dt_local = sprint_dt.astimezone(local_timezone)
        sprint_date = sprint_dt_local.date().strftime('%d.%m.%Y')
        sprint_time = sprint_dt_local.time().strftime('%H:%M')
        sprint_day = sprint_dt_local.weekday()
        sprint_day = day_names[sprint_day]
        embed.add_field(name="Sprint:", value=f'{sprint_date} ({sprint_day}) godz. {sprint_time}', inline=False)

    race_date = race['date']
    race_time = race['time']
    # race time is in UTC
    race_dt_str = f'{race_date}T{race_time}'
    race_dt = dt.datetime.strptime(race_dt_str, '%Y-%m-%dT%H:%M:%SZ')
    race_dt_local = race_dt.astimezone(local_timezone)
    race_date = race_dt_local.date().strftime('%d.%m.%Y')
    race_time = race_dt_local.time().strftime('%H:%M')
    race_day = race_dt_local.weekday()
    race_day = day_names[race_day]
    embed.add_field(name="Wyścig:", value=f'{race_date} ({race_day}) godz. {race_time}', inline=False)

    return embed
