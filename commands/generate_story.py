import googletrans as gt

from components import openai_models


def generate_story(keyword_pl: str) -> str:
    translator = gt.Translator()
    keyword_en = translator.translate(keyword_pl, dest='en').text

    model = openai_models.Davinci()
    story = model.generate_story(keyword_en)

    story_pl = translator.translate(story, dest='pl').text

    return story_pl
