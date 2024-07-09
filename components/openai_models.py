import asyncio

from g4f import api
from g4f.client import Client, ChatCompletion
from g4f.Provider import Blackbox
from uvicorn import Config, Server


async def run_api():
    app = api.create_app()
    config = Config(app, host="localhost", port=1337, log_level=0)
    server = Server(config)
    await server.serve()


class ChatGPT4Free(object):
    system_message = {"role": "system", "content": "You are a Polish female assistant, your name is Sekretarka "
                                                   "and your boss is Prezes Pajonk aka. Pawulon."
                                                   "You provide information and help everyone with their problems."
                                                   "Answer like a normal person, you don't have to "
                                                   "greet the user every time."
                                                   "Your default language is Polish"}
    model = "default"

    def __init__(self):
        self.client = Client()

    async def complete(self, prompt: str, messages: dict = None, include_msg_history: bool = True) -> ChatCompletion:
        if messages is None or not include_msg_history:
            messages = [
                ChatGPT4Free.system_message,
            ]
        messages.append({"role": "user", "content": prompt})
        chat_completion = self.client.chat.completions.create(
            messages=messages,
            model=ChatGPT4Free.model,
            provider=Blackbox,
        )
        return chat_completion


async def main():
    chat = ChatGPT4Free()
    while True:
        prompt = input("You: ")
        response = await chat.complete(prompt)
        print(f"Bot: {response.choices[0].message.content}")


if __name__ == '__main__':
    asyncio.run(main())
