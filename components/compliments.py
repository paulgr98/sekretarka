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

    if username == 'panpajonk':
        compliments.append('Twoja dziewczyna jest jak pierwiastek z -100. Solidna 10, ale urojona xD')
        compliments.append('Tobie już nie potrzeba komplementów przystojniaku UwU')


    if username == 'marta.6442':
        compliments.append('Kiedy się uśmiechasz, słońce ma kompleksy, bo nie potrafi być tak jasne jak Ty :sunny:')
        compliments.append('Jesteś jak kawa. Gorąca, słodka i pobudzająca :coffee: :smirk:')
        compliments.append('Twój wzrok ma taką moc, że nawet Superman by stracił swoje supermoce :superhero: :heart:')
        compliments.append('Jesteś dla mnie jak ulubiony utwór - mogę Cię słuchać na okrągło, '
                           'a i tak nie mam dość :heart: :notes:')
        compliments.append('Czy jesteś czarodziejką? Bo kiedy się uśmiechasz, '
                           'wszystko dookoła magicznie staje się lepsze :magic_wand: :sparkles:')
        compliments.append('Czy jesteś matematyką? Bo dodajesz wartość do mojego życia, '
                           'odejmujesz smutek, mnożysz radość i dzielisz moje problemy UwU :heart:')
        compliments.append('Gdybym była sędzią, uznałabym Cię winną za bycie zbyt hot :hot_face:')
        compliments.append('Czy jesteś serwisem lex.pl? Bo masz w sobie wszystko, czego szukam :scales: :smirk:')
        compliments.append('Tyś jest jak bryndza - miękka, słodka i zawsze dobrze smakuje :heart:')
        compliments.append('Czy jesteś jak goździk? Bo jak cię patrzę, to aż mi serce szpuntuje :heart:')
        compliments.append('Wiesz, co jest różnica między tobą a kartoflami? Kartofle zjem na obiad, '
                           'a tobą chciałbym się delektować cały dzień :smirk: :potato:')
        compliments.append('Twój uśmiech jest jak słońce, które oświeca moje szare dni - '
                           'jak na lampach lejcht :diya_lamp:')
        compliments.append('Czy wiesz, że zgodnie z art. 446 § 4 Kodeksu cywilnego, mogę Cię obciążyć obowiązkiem '
                           'zaspokojenia mojego cierpienia? Bo każda chwila bez Ciebie jest dla mnie męką')
        compliments.append('Art. 118 Kodeksu wykroczeń mówi o zakłócaniu ciszy nocnej. Ale co jeśli to moje bijące '
                           'serce nie pozwoli mi zachować ciszy, gdy o Tobie myślę?')
        compliments.append('Zgodnie z art. 231 Kodeksu karnego, przekroczenie uprawnień to przestępstwo. Ale Ty '
                           'przekraczasz granice mojego serca bez żadnej kary')
        compliments.append('Art. 24 Kodeksu cywilnego mówi, że każdy ma prawo do poszanowania swojego życia '
                           'prywatnego. Ale ja chciałbym, abyś stała się najważniejszą częścią mojego')
        compliments.append('Czy wiesz, że zgodnie z art. 415 Kodeksu karnego, zaniedbanie obowiązku jest karalne? '
                           'Obawiam się, że zaniedbałem obowiązek powiedzenia Ci, jak bardzo Cię adoruję')
        compliments.append('Zgodnie z art. 58 Kodeksu cywilnego, zobowiązania nie mogą być spełnione przez osoby '
                           'trzecie. Ale moje uczucia do Ciebie są tak silne, że nikt inny nie mógłby ich spełnić')
        compliments.append('Art. 86 Kodeksu pracy mówi o prawie do równego traktowania w zatrudnieniu. Ale ja nie '
                           'chcę Cię traktować jak równe - dla mnie jesteś wyjątkowa')
        compliments.append('Art. 155 Kodeksu karnego mówi o nieumyślnym spowodowaniu śmierci. Ale Ty swoim uśmiechem '
                           'nieumyślnie zabijasz mnie każdego dnia')
        compliments.append('Art. 12 Kodeksu postępowania cywilnego mówi o zasadach rozstrzygania spraw. Ale jedyna '
                           'sprawa, którą chciałbym rozstrzygnąć, to kiedy mogę znowu zobaczyć Twój uśmiech')

    return compliments
