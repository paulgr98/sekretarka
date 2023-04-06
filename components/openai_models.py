import config as cfg
import openai
from openai.error import RateLimitError


class Davinci(object):
    def __init__(self):
        openai.api_key = cfg.OPENAI_API_KEY
        self.model = openai.Completion()

    def complete(self, prompt: str) -> str:
        completions = self.model.create(
            engine="text-davinci-002",
            prompt=prompt,
            max_tokens=2048,
            n=1,
            stop=None,
            temperature=0.5,
        )

        message = completions.choices[0].text
        return message

    def generate_story(self, keywords: str) -> str:
        prompt = f'Write a story about {keywords}.'
        story = self.complete(prompt)
        return story


class ChatGPT(object):
    def __init__(self):
        openai.api_key = cfg.OPENAI_API_KEY

    def complete(self, prompt: str) -> str:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        content: str = completion.choices[0].message["content"]
        return content
