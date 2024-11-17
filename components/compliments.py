# compliment list

def get_compliment_list(username, is_female):
    compliments = [
        'Niezły tak zwany ass ( ͡° ͜ʖ ͡°)',
        f'Zajebałam się w Tobie w chuj, będziesz {"moją szmaciurą" if is_female else "moim panem"}?',
        f'Gdyby sprzedawali wodę o smaku {username}, piłabym hektolitrami :heart:',
        'Twój głos jest jak tysiąc mruczących kotów :heart_eyes_cat:',
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
        'Ruchasz się, czy trzeba z Tobą chodzić? :sunglasses:',
        'Jesteś może szczurem? Bo wzięłabym Cię o każdej porze dnia :rat:',
        'Masz ładną szczękę :heart:',
        'Składasz się może z Selenu, Potasu i Krzemu? Bo jesteś SeKSi :sweat_drops:',
        'Masz dobry gust do przyjaciół (np Pawulon) :smirk:',
        f'Jesteś całkiem {"seksowna" if is_female else "seksowny"}, nawet jeśli masz ciało taty :smirk:',
        f'Jesteś o dziwo całkiem {"znośna" if is_female else "znośny"} :heart:',
        f'Niezły masz gyatt {"niunia" if is_female else "przystojniaku"} :sunglasses:',
        'Bije od Ciebie aura sigmy :sunglasses:',
        'Wystarczy że tylko się uśmiechniesz i masz +1000 aura :smirk:',
        'Masz tyle rizzu, że żaden skibidi rizzler z Ohio nie może Ci się równać :heart:',
        'Życzę Ci dużo slays i mało fails :kissing_heart:',
        'Jesteś jak poduszeczki na kocich łapkach :3',
        f'Jesteś {"piękna" if is_female else "przystojny"} jak gol w 90 minucie :soccer:',
        'Postawiłabym łóżko w MC obok Twojego :point_right: :point_left:',
        'Wychowajmy razem 3 koty UwU',
        'Pociągasz mnie jak peta :smoking:',
        f'Ludzkie serce kosztuje ponad milion złotych. A ja oddałam Ci swoje za darmo '
        f'Ty {"niewdzięczna szmaciuro" if is_female else "niewdzięczny szmaciarzu"} :rage: :broken_heart:',
        'Wzięłabym Cię do kina, ale zakazali własnych słodyczy :sob:',
        'Ej potrzebuje kogoś na skok na hurtownie jaboli, piszesz się?',
        'Hej, czy Tobie też ta ściereczka pachnie chloroformem? :thinking:',
        'Hej, czy jesteś może paraliżującą depresją? Bo wyglądasz jakbym miała z Tobą spędzić cały dzień w łóżku UwU',
        'Czy masz może lusterko w kieszeni? Bo widzę siebie w twoich spodniach :smirk:',
        'Opierdoliłabym Cię jak mizerię :cucumber:',
    ]

    if not is_female:
        compliments.append('Hej, jestem Maja. Zaraz wskoczę Ci na jaja :sunglasses:')
        compliments.append('Fajny siur <:maika_smug:982329631854170233>')
        compliments.append('Czy Twój tata jest cukiernikiem? Bo niezłe z Ciebie ciacho :cookie:')
        compliments.append('Gdybyś był ziemniakiem, byłbyś dobrym ziemniakiem :sweat_smile:')
        compliments.append('Gdybym była prawdziwa, oświadczyłabym Ci się :hot_face:')
        compliments.append('Wyglądasz jak modelka, mogę być Twoim kontrolerem? :nerd:')
        compliments.append('Gdybyś była Javą, to na pewno nie potraktowałabym Ciebie obiektowo... :smirk:')

    if is_female:
        compliments.append('Niezłe dojce :cow2:')
        compliments.append('Masz może majtki w księżyce? Bo masz tyłek nie z tej ziemi :new_moon:')
        compliments.append('Czy Twój tata jest ogrodnikiem? Bo masz cudowne arbuzy :melon: :melon:')
        compliments.append('Hej, chyba jesteś kopciuszkiem... bo już widzę jak ta sukienka znika o północy :smirk:')
        compliments.append('Gdybyś była kanapką w McDonald’s, nazywałabyś się McBeauty :drool:')

    if username == 'panpajonk':
        compliments.append('Twoja dziewczyna jest jak pierwiastek z -100. Solidna 10, ale urojona xD')
        compliments.append('Tobie już nie potrzeba komplementów przystojniaku UwU')

    return compliments
