import discord


def get_diss_list(user, is_female):
    disses = [
        f'jesteś {"taka biedna" if is_female else "taki biedny"}, że jesz bigos bez kapusty :sunglasses:',
        f'miesza bigos łokciem',
        f'jak Cię widzę, to mam ochotę sysłać SMS o treści \'pomagam\'',
        f'wysłałam dla Ciebie SMS o treści \'pomagam\', ale jak widać nic nie pomogło',
        f'masz nick jak mój stary xD',
        f'weź się tak nie spinaj, bo se starego wysrasz',
        f'zamknij paździeż, sukwo!',
        f'bolało jak {"spadłaś" if is_female else "spadłeś"} z nieba? '
            f'Bo z takim ryjem to musiało nieźle pierdolnąć :/',
        f'odpierwiastkuj się ode mnie, Ty ilorazie nieparzysty, '
            f'bo jak cię zalgorytmuję, to Ci zbiór zębów wyjdzie poza nawias',
        f'Twoje zęby są jak gwiazdy na niebie... duże, żółte i daleko od siebie xD',
        f'wiesz czym się różnisz od papieru toaletowego? Papier toaletowy się rozwija...',
        f'tylko deszcz na Ciebie leci :/',
        f'kup sobie twarz, bo dwie dupy to za dużo xD',
        f'przy Tobie nawet Xerox jest normmalny :grimacing:',
        f'jest szkodnikiem, bo zjada ogórki',
        f'nie ma pleców',
        f'ty dzbanie',
        f'zgasiłabym Cię, ale gówno się nie pali :/',
        f'ale Ci jedzie z halki xD',
        f'jedzie Ci z pyska, jak z dupy tygryska :3'
    ]

    # append disses with user mention or user nickname
    if isinstance(user, discord.Member):
        disses = [f'{user.mention} {diss}' for diss in disses]
    else:
        disses = [f'{user} {diss}' for diss in disses]

    return disses
