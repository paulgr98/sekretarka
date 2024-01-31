from components import openai_models
import asyncio


async def generate_story(keyword_pl: str) -> str:
    gpt = openai_models.ChatGPT4Free()
    story_task = asyncio.create_task(gpt.complete(f"Napisz krótkie opowiadanie o {keyword_pl}"))
    story = await story_task
    return story
