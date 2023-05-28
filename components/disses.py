import discord


def get_diss_list(user, is_female):
    disses = [
        f'jesteś {"taka biedna" if is_female else "taki biedny"}, że jesz bigos bez kapusty :sunglasses:',
        'miesza bigos łokciem',
        'jak Cię widzę, to mam ochotę wysłać SMS o treści \'pomagam\'',
        'wysłałam dla Ciebie SMS o treści \'pomagam\', ale jak widać nic nie pomogło',
        'masz nick jak mój stary',
        'weź się tak nie spinaj, bo se starego wysrasz',
        'zamknij paździeż, sukwo!',
        f'bolało jak {"spadłaś" if is_female else "spadłeś"} z nieba? '
        'Bo z takim ryjem to musiało nieźle pierdolnąć :/',
        'odpierwiastkuj się ode mnie, Ty ilorazie nieparzysty, '
        'bo jak cię zalgorytmuję, to Ci zbiór zębów wyjdzie poza nawias',
        'Twoje zęby są jak gwiazdy na niebie... duże, żółte i daleko od siebie',
        'wiesz czym się różnisz od papieru toaletowego? Papier toaletowy się rozwija...',
        'tylko deszcz na Ciebie leci :/',
        'kup sobie twarz, bo dwie dupy to za dużo',
        'jest szkodnikiem, bo zjada ogórki',
        'nie ma pleców',
        'ty dzbanie',
        'zgasiłabym Cię, ale gówno się nie pali :/',
        'jedzie Ci z pyska, jak z dupy tygryska'
    ]

    # append disses with user mention or user nickname
    if isinstance(user, discord.Member):
        disses = [f'{user.mention} {diss}' for diss in disses]
    else:
        disses = [f'{user} {diss}' for diss in disses]

    return disses
