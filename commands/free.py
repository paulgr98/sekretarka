import discord
import datetime as dt


def make_game_embed(game: dict, period: str) -> discord.Embed:
    embed = discord.Embed(title=game['title'], color=0x571E1E)
    embed.set_thumbnail(url=game['keyImages'][2]['url'])
    embed.add_field(name='Opis', value=game['description'], inline=False)
    scope = 'promotionalOffers' if period == 'current' else 'upcomingPromotionalOffers'
    from_time_raw = game['promotions'][scope][0]['promotionalOffers'][0]['startDate']
    from_time = dt.datetime.strptime(from_time_raw, '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%d.%m.%Y %H:%M')
    embed.add_field(name='Od', value=from_time, inline=False)
    to_time_raw = game['promotions'][scope][0]['promotionalOffers'][0]['endDate']
    to_time = dt.datetime.strptime(to_time_raw, '%Y-%m-%dT%H:%M:%S.%fZ').strftime('%d.%m.%Y %H:%M')
    embed.add_field(name='Do', value=to_time, inline=False)

    return embed
