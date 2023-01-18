import discord


def get_help_embed(prefix: str) -> discord.Embed:
    embed = discord.Embed(title="Pomoc", description="Lista komend", color=0x00ff00)
    embed.add_field(name=f"{prefix}ping",
                    value="Testuje połącznie",
                    inline=False)
    embed.add_field(name=f"{prefix}hi",
                    value="Wita się",
                    inline=False)
    embed.add_field(name=f"{prefix}purge [ilość=2]",
                    value="Usuwa [ilość] wiadomości wyżej. Domyślnie, bez podawania jawnie, ilość=2",
                    inline=False)
    embed.add_field(name=f"{prefix}undo [ilość=1]",
                    value="Usuwa [ilość] ostatnich wiadomości bota. Domyślnie, bez podawania jawnie, ilość=1",
                    inline=False)
    embed.add_field(name=f"{prefix}compliment [użytkownik=None]",
                    value="Daje komplement użytkownikowi [użytkownik] jeśli podany, lub autorowi, jeśli nie podany ",
                    inline=False)
    embed.add_field(name=f"{prefix}diss [użytkownik=None]",
                    value="Dissuje użytkownikowi [użytkownik] jeśli podany, lub autorowi, jeśli nie podany ",
                    inline=False)
    embed.add_field(name=f"{prefix}demote",
                    value="Demotywuje do życia (jakby samo życie nie wystarczało)",
                    inline=False)
    embed.add_field(name=f"{prefix}rdt [sub=memes] [limit=100]",
                    value="Wyświetla losowy obrazek z reddita na subreddicie [sub], losując spośród [limit] "
                          "najpopularniejszych obrazków",
                    inline=False)
    embed.add_field(name=f"{prefix}astro [znak]",
                    value="Wyświetla horoskop dla znaku [znak]",
                    inline=False)
    embed.add_field(name=f"{prefix}nameday",
                    value="Wyświetla imieniny dla obecnego dnia",
                    inline=False)
    embed.add_field(name=f"{prefix}wthr [miasto=Warszawa] [dni=0]",
                    value="Wyświetla prognozę pogody dla miasta [miasto], za [dni] dni",
                    inline=False)
    embed.add_field(name=f"{prefix}drink [nazwa drinka=None]",
                    value="Wyświetla losowy przepis na drinka, lub konkretny, jeśli podany",
                    inline=False)
    embed.add_field(name=f"{prefix}free [okres=current]",
                    value="Wyświetla listę darmowych gier z Epic Games Store, w okresie [okres]. Możliwe wartości: "
                          "current, upcoming",
                    inline=False)
    embed.add_field(name=f"{prefix}gif [fraza]",
                    value="Wyświetla losowy GIF z frazą [fraza]",
                    inline=False)
    embed.add_field(name=f"{prefix}topgif [fraza]",
                    value="Wyświetla najpopularniejszy GIF z frazą [fraza]",
                    inline=False)
    embed.add_field(name=f"{prefix}shipme",
                    value="Wyświetla ship dla Ciebie",
                    inline=False)
    embed.add_field(name=f"{prefix}shipstat",
                    value="Wyświetla użytkownika, z którym masz największą liczbę shipów",
                    inline=False)
    embed.add_field(name=f"{prefix}roll [minimum=1] [maximum=6]",
                    value="Wyświetla losową liczbę między [minimum] a [maximum]",
                    inline=False)
    embed.add_field(name=f"{prefix}coin",
                    value="Rzuca monetą i wyświetla wynik (orzeł albo reszka)",
                    inline=False)
    embed.add_field(name=f"{prefix}sw [start/stop/reset]",
                    value="Uruchamia stoper, zatrzymuje go, lub resetuje",
                    inline=False)
    embed.add_field(name=f"{prefix}inactive",
                    value="Wyświetla TOP 5 najmniej aktywnych użytkowników",
                    inline=False)
    embed.add_field(name=f"{prefix}poll [treść]; [odp1]; [odp2]; ...",
                    value="Tworzy ankietę z podanych opcji. Treść i opcje muszą być oddzielone ;",
                    inline=False)
    embed.add_field(name=f"{prefix}essa [użytkownik=None]",
                    value="Wyświetla esse użytkownika [użytkownik] jeśli podany, lub autorowi, jeśli nie podany ",
                    inline=False)
    embed.add_field(name=f"{prefix}convert [metoda] [tekst]",
                    value="Konwertuje tekst [tekst] metodą [metoda]. Możliwe wartości: "
                          "s2b, b2s, s2h, h2s, s2b64, b642s",
                    inline=False)
    embed.add_field(name=f"{prefix}uwu",
                    value="UwUalizuje wiadomość wyżej",
                    inline=False)
    embed.add_field(name=f"{prefix}ban [użytkownik]",
                    value="Banuje użytkownika [użytkownik]",
                    inline=False)
    
    return embed
