from components import f1
import discord


def make_next_race_embed():
    current_dt = f1.get_now_time()
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

    day_names = {0: 'Poniedziałek', 1: 'Wtorek', 2: 'Środa', 3: 'Czwartek', 4: 'Piątek', 5: 'Sobota', 6: 'Niedziela'}

    quali_date = race['Qualifying']['date']
    quali_time = race['Qualifying']['time']
    quali_dt_local = f1.str_to_local_dt(quali_date, quali_time)
    quali_date = quali_dt_local.date().strftime('%d.%m.%Y')
    quali_time = quali_dt_local.time().strftime('%H:%M')
    quali_day = quali_dt_local.weekday()
    quali_day = day_names[quali_day]
    quali_time_left = quali_dt_local - current_dt
    quali_time_left = f1.timedelta_to_str(quali_time_left)
    embed.add_field(name="Kwalifikacje:", value=f'{quali_date} ({quali_day}) godz. {quali_time}\n'
                                                f'[za {quali_time_left}]', inline=False)

    if 'Sprint' in race:
        sprint_date = race['Sprint']['date']
        sprint_time = race['Sprint']['time']
        sprint_dt_local = f1.str_to_local_dt(sprint_date, sprint_time)
        sprint_date = sprint_dt_local.date().strftime('%d.%m.%Y')
        sprint_time = sprint_dt_local.time().strftime('%H:%M')
        sprint_day = sprint_dt_local.weekday()
        sprint_day = day_names[sprint_day]
        sprint_time_left = sprint_dt_local - current_dt
        sprint_time_left = f1.timedelta_to_str(sprint_time_left)
        embed.add_field(name="Sprint:", value=f'{sprint_date} ({sprint_day}) godz. {sprint_time}\n'
                                              f'[za {sprint_time_left}]', inline=False)

    race_date = race['date']
    race_time = race['time']
    race_dt_local = f1.str_to_local_dt(race_date, race_time)
    race_date = race_dt_local.date().strftime('%d.%m.%Y')
    race_time = race_dt_local.time().strftime('%H:%M')
    race_day = race_dt_local.weekday()
    race_day = day_names[race_day]
    race_time_left = race_dt_local - current_dt
    race_time_left = f1.timedelta_to_str(race_time_left)
    embed.add_field(name="Wyścig:", value=f'{race_date} ({race_day}) godz. {race_time}\n'
                                          f'[za {race_time_left}]', inline=False)

    return embed
