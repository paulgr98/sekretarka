# compliment list

def get_compliment_list(username, is_female):
    compliments = [
        f'{"Nudna" if is_female else "Nudny"} jesteś, nara :unamused:',
        'Niezły tak zwany ass ( ͡° ͜ʖ ͡°)',
        f'Zajebałam się w Tobie w chuj, będziesz {"moją szmaciurą" if is_female else "moim panem"}?',
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
        compliments.append('Hej, jestem Maja. Zaraz wskoczę Ci na jaja :sunglasses:')
        compliments.append('Fajny siur <:maika_smug:982329631854170233>')
        compliments.append('Czy Twój tata jest cukiernikiem? Bo niezłe z Ciebie ciacho :cookie:')
        compliments.append('Gdybyś był ziemniakiem, byłbyś dobrym ziemniakiem :sweat_smile:')
        compliments.append('Gdybym była prawdziwa, oświdczyłabym Ci się :hot_face:')

    if is_female:
        compliments.append('Pokasz stupki pls :hot_face:')
        compliments.append('Niezłe dojce :cow2:')
        compliments.append('Masz może majtki w księżyce? Bo masz tyłek nie z tej ziemi :new_moon:')
        compliments.append('Czy Twój tata jest ogrodnikiem? Bo masz cudowne arbuzy :melon: :melon:')
        compliments.append('Hej, chyba jesteś kopciuszkiem... bo już widzę jak ta sukienka znika o północy :smirk:')
        compliments.append('Gdybyś była kanapką w McDonald’s, nazywałabyś się McBeauty :drool:')
        compliments.append('Chodź zabawimy się w dom. Ty będziesz drzwiami, a ja będę pukała! :smiling_imp:')

    if username == 'PanPajonk':
        compliments.append('Twoja dziewczyna jest jak pierwiastek z -100. Solidna 10, ale urojona xD')
        compliments.append('Tobie już nie potrzeba komplementów przystojniaku UwU')

    return compliments
