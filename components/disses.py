
def get_diss_list(user, is_female):
    disses = [
        f'{user.mention} jesteś {"taka biedna" if is_female else "taki biedny"}, że jesz bigos bez kapusty :sunglasses:',
        f'{user.mention} miesza bigos łokciem'
        f'{user.mention} jak Cię widzę, to mam ochotę sysłać SMS o treści \'pomagam\'',
        f'{user.mention} wysłałam dla Ciebie SMS o treści \'pomagam\', ale jak widać nic nie pomogło',
        f'{user.mention} masz nick jak mój stary xD',
        f'{user.mention} weź się tak nie spinaj, bo se starego wysrasz',
        f'{user.mention} zamknij paździeż, sukwo!',
        f'{user.mention} bolało jak {"spadłaś" if is_female else "spadłeś"} z nieba? '
            f'Bo z takim ryjem to musiało nieźle pierdolnąć :/',
        f'{user.mention} odpierwiastkuj się ode mnie, ty ilorazie nieparzysty, '
            f'bo jak cię zalgorytmizuję, to ci zbiór zębów wyjdzie poza nawias',
        f'{user.mention} Twoje zęby są jak gwiazdy na niebie... duże, żółte i daleko od siebie xD',
        f'{user.mention} wiesz czym się różnisz od papieru toaletowego? Papier toaletowy się rozwija...',
        f'{user.mention} tylko deszcz na Ciebie leci :/',
        f'{user.mention} kup sobie twarz, bo dwie dupy to za dużo xD',
        f'{user.mention} przy Tobie nawet Xerox jest normmalny :grimacing:'
        f'{user.mention} jest szkodnikiem, bo zjada ogórki',
        f'{user.mention} nie ma pleców',
        f'{user.mention} ty dzbanie',
        f'{user.mention} zgasiłabym Cię, ale gówno się nie pali :/',
    ]

    return disses
