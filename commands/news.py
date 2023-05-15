import discord

from components import news_feed
from components.openai_models import ChatGPT


def get_description_from_url(url: str) -> str:
    gpt = ChatGPT()
    res = gpt.complete(f'Opisz ten artykuł w 2 zdaniach: {url}')
    return res


def get_news_embeds(number: int = 5) -> list[discord.Embed]:
    tvn24 = news_feed.Tvn24Feed()
    tvn24.set_src_to_important()
    news = tvn24.get_news()
    embeds = []
    for event in news[:number]:
        description = get_description_from_url(event['link'])
        embed = discord.Embed(title=event['title'], url=event['link'], description=description)
        embeds.append(embed)

    return embeds
