import discord


def init_cap(s: str) -> str:
    return s[0].upper() + s[1:]


def format_options(options: list) -> tuple[str, list]:
    number_emojis = [f"{num}\N{COMBINING ENCLOSING KEYCAP}" for num in range(1, 10)]

    opt_str = ''
    reactions = []

    for i, opt in enumerate(options):
        opt_str += f'{number_emojis[i]} {opt}\n'
        reactions.append(number_emojis[i])

    return opt_str, reactions


def create_embed(title: str, options: list) -> tuple[discord.Embed, list]:
    opt_str, reactions = format_options(options)

    embed = discord.Embed(title=title, color=0x571E1E)
    embed.add_field(name='Odpowiedzi', value=opt_str, inline=False)

    return embed, reactions
