import g4f
from g4f.Provider import Bing, You
from g4f.models import default
import g4f.api
import openai

import config as cfg
import asyncio
from threading import Thread


async def run_api():
    g4f.api.Api(engine=g4f, debug=False).run(ip="127.0.0.1:1337")


class ChatGPT(object):
    def __init__(self):
        openai.api_key = cfg.OPENAI_API_KEY

    @staticmethod
    def complete(prompt: str) -> str:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        content: str = completion.choices[0].message["content"]
        return content


class ChatGPT4Free(object):
    system_message = {"role": "system", "content": "You are a Polish female assistant, your name is Sekretarka "
                                                   "and your boss is Prezes Pajonk aka. Pawulon."
                                                   "Your default language is Polish"}
    provider = Bing
    model = "gpt-4"

    def __init__(self):
        self.client = openai.OpenAI(api_key=cfg.HUGGINGFACE_API_KEY, base_url="http://localhost:1337/v1")

    async def complete(self, prompt: str, messages: dict = None) -> str:
        if messages is None:
            messages = [
                ChatGPT4Free.system_message,
            ]
        messages.append({"role": "user", "content": prompt})
        chat_completion = g4f.ChatCompletion.create(
            model=ChatGPT4Free.model,
            messages=messages,
            provider=ChatGPT4Free.provider,
        )
        return chat_completion


async def main():
    chat = ChatGPT4Free()
    while True:
        prompt = input("You: ")
        response = await chat.complete(prompt)
        print(f"Bot: {response}")


if __name__ == '__main__':
    # run api on other thread
    api_thread = Thread(target=asyncio.run, args=(run_api(),))
    api_thread.start()

    # run main
    asyncio.run(main())
