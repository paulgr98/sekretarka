import discord

from components import f1


class EventDetails:
    def __init__(self, event, event_name, current_dt):
        self.event = event
        self.event_name = event_name
        self.current_dt = current_dt


def format_event_time(event_details) -> tuple:
    day_names = {0: 'Poniedziałek', 1: 'Wtorek', 2: 'Środa', 3: 'Czwartek', 4: 'Piątek', 5: 'Sobota', 6: 'Niedziela'}
    event_date = event_details.event['date']
    event_time = event_details.event['time']
    event_dt_local = f1.str_to_local_dt(event_date, event_time)
    event_date_str = event_dt_local.date().strftime('%d.%m.%Y')
    event_time_str = event_dt_local.time().strftime('%H:%M')
    event_day = day_names[event_dt_local.weekday()]
    event_time_left = f1.timedelta_to_str(event_dt_local - event_details.current_dt)

    event_name_str = f'{event_details.event_name}:\n'
    event_time_str = (f'- {event_date_str} ({event_day})\n'
                      f'- godz. {event_time_str}\n'
                      f'- za {event_time_left}')
    return event_name_str, event_time_str


def add_event_field(embed, event_details):
    event_name, event_time = format_event_time(event_details)
    embed.add_field(name=event_name, value=event_time, inline=False)


def add_blank_line(embed):
    embed.add_field(name="\u200B", value="", inline=False)


def make_next_race_embed():
    current_dt = f1.get_now_time()
    race = f1.get_next_race(current_dt)

    race_round = race['round']
    race_name = race['raceName']
    embed = discord.Embed(
        title=f'#{race_round} {race_name}',
        colour=0xff2800
    )
    embed.add_field(name="Tor:", value=race['Circuit']['circuitName'], inline=False)

    if 'SprintQualifying' in race:
        add_blank_line(embed)
        add_event_field(embed, EventDetails(race['SprintQualifying'], "Kwalifikacje Sprintu", current_dt))

    if 'Sprint' in race:
        add_blank_line(embed)
        add_event_field(embed, EventDetails(race['Sprint'], "Sprint", current_dt))

    add_blank_line(embed)
    add_event_field(embed, EventDetails(race['Qualifying'], "Kwalifikacje", current_dt))

    add_blank_line(embed)
    add_event_field(embed, EventDetails(race, "Wyścig", current_dt))

    return embed
