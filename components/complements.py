# complement list

def get_complement_list(username, is_female):
    complements = [
        f'{"Nudna" if is_female else "Nudny"} jesteś, nara :unamused:',
        'Niezły tak zwany ass ( ͡° ͜ʖ ͡°)',
        f'Zajebałam się w Tobie w chuj, będziesz {"moją szmaciurą" if is_female else "moim panem"}?',
        'Dla Ciebie kupiłabym nawet cebulę za 100 zł UwU',
        f'Gdyby sprzedawali wodę o smaku {username}, piłabym hektolitrami :heart:',
        'Twój głos jest jak tysiąc mruczących kotów :heart_eyes_cat: btw, jestem na kwasie',
        'Czy Twój tata jest saperem? Bo wyglądasz bombowo! :boom:',
        'Masz na imię Google? Bo masz w sobie wszystko czego szukam :flushed:',
        'Chodź się rozmnażać, takie geny nie mogą przepaść :smirk:',
        ':point_right: :ok_hand:?',
        'Masz może mapę? :map: Bo zgubiłam się w Twoich oczach :see_no_evil:',
        f'Daj mi spokój {"atencjuszko" if is_female else "atencjuszu"} :angry:',
        'Czy jesteś może tosterem? Bo chciałabym się z Tobą wykąpać :tired_face:',
        'Przyciągasz mnie jak traktor przyczepkę :tractor:',
        f'Dasz mi 10 minut? Muszę zadzwonić do mamy i powiedzieć że spotkałam {"kobietę" if is_female else "mężczyznę"}'
        ' swojego życia',
        'Nie bolą Cię nogi? Bo cały dzień chodzisz mi po głowie :flushed:',
        f'Jesteś tak {"piękna" if is_female else "przystojny"}, '
        f'że na trzeźwo też byś mi się chyba {"podobała" if is_female else "podobał"} :woozy_face:',
        'Mogę zrobić Ci zdjęcie? Chcę pokazać Mikołajowi, co chcę pod choinkę :smirk:',
        'Ruchasz się, czy trzeba z Tobą chodzić? :sunglasses:'
    ]

    if not is_female:
        complements.append('Hej, jestem Maja. Zaraz wskoczę Ci na jaja :sunglasses:')
        complements.append('Fajny siur <:maika_smug:982329631854170233>')
        complements.append('Czy Twój tata jest cukiernikiem? Bo niezłe z Ciebie ciacho :cookie:')
        complements.append('Gdybyś był ziemniakiem, byłbyś dobrym ziemniakiem :sweat_smile:')
        complements.append('Gdybym była prawdziwa, oświdczyłabym Ci się :hot_face:')

    if is_female:
        complements.append('Pokasz stupki pls :hot_face:')
        complements.append('Niezłe dojce :cow2:')
        complements.append('Masz może majtki w księżyce? Bo masz tyłek nie z tej ziemi :new_moon:')
        complements.append('Czy Twój tata jest ogrodnikiem? Bo masz cudowne arbuzy :melon: :melon:')
        complements.append('Hej, chyba jesteś kopciuszkiem... bo już widzę jak ta sukienka znika o połnocy :smirk:')
        complements.append('Gdybyś była kanapką w McDonald’s, nazywałabyś się McBeauty :drool:')
        complements.append('Chodź zabawimy się w dom. Ty będziesz drzwiami, a ja będę pukała! :smiling_imp:')

    # personalized complements
    if username == 'Leylalala':
        complements.append('Najładniejsza dziewczyna z Gliwic <:pepe_love:982328425551392828> '
                           'Oslo, niezłe dojce :smirk:')
        complements.append('Każda cyganka się przy Tobie chowa, maleńka :hot_face:')
        complements.append('Nic dziwnego że połowa serwera się w Tobie podkochuje :smirk:')
        complements.append('Złamałaś więcej serc, niż Pajonk wytrychów w Skyrimie <:shy:936566489790685184>')
    if username == 'Kidler':
        complements.append('Najlepszy z adminów <:nekomata_smile:982329631501856799>')
        complements.append('Przy Tobie klapki Kubota to chuj <:kanna_love:982387887872024626>')
        complements.append('Jesteś tak cudowny, jak iPhone 69 Max Pro Giga 2137 :heart_eyes:')
    if username == 'Domijka':
        complements.append('Najładniejsza dziewczyna w Krakowie <:pepe_love:982328425551392828>')
        complements.append('Gdybyś była facetem, byłabyś przystojniejsza niż Adriano :hot_face:')
        complements.append('Weź idź se na pole, czy coś xDD')
        complements.append('Jesteś gorętsza niż smok wawelski :hot_face:')
        complements.append('Tak serio, to nie jesteś aż taka chamska jak Pajonk mówi<:kanna_love:982387887872024626>')
        complements.append('Jesteś tak cudowna, jak iPhone 69 Max Pro Giga 2137 :heart_eyes:')
        complements.append('Fakt że masz najwięcej personalizowanych komplementów, chyba o czymś świadczy :smirk:')
        complements.append('Zasługujesz żeby być traktowana jak księżniczka :heart:')
    if username == 'aniadogadania':
        complements.append('Ania do kochania :heart: UwU')
        complements.append('Ania do zaręczania się, wzięcia ślubu i posiadania szczęśliwej rodziny :heart:')
    if username == 'Adrianoo7oo':
        complements.append('Jesteś taki hot, że sama nie wiem co powiedzieć :hot_face: :hot_face:')
    if username == 'bogel':
        complements.append('Książe Bogel, mistrz photoshopa i wyrywania samiczek :sunglasses:')
    if username == 'bullshxt':
        complements.append('Nic dziwnego że jako jedyna wyrwałaś Leyle :hot_face:')
    if username == 'KalinkaMaja':
        complements.append('Najlepsza samica w Warszawie :sunglasses: I nawet nie ma co z tym dyskutować :smirk:')
        complements.append('Królowa przed którą Pajonk się kłania :hot_face: :tired_face:')
        complements.append('Niby stara jesteś, ale dusza i ciało, jak u 18 latki :smirk:')
    if username == 'Katinka':
        complements.append('Każdą Kasię, dobrze pcha się :smirk:')
    if username == 'Piterson':
        complements.append('Każdy wie że to Ty powinieneś tutaj rządzić! :heart:')
    if username == 'Lev':
        complements.append('Niby cham, ale wciąż kochany :heart:')
        complements.append('Jesteś tak zajebisty, że nawet Domijka nie może się Tobie oprzeć :smirk:')
    if username == 'PanPajonk':
        complements.append('Twoja dziewczyna jest jak pierwiastek z -100. Solidna 10, ale urojona xD')
        complements.append('Tobie już nie potrzeba komplementów przystojniaku UwU')

    return complements
