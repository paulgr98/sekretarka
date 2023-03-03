from components import openai_models
import googletrans as gt


def generate_story(keyword_pl: str) -> str:
    translator = gt.Translator()
    keyword_en = translator.translate(keyword_pl, dest='en').text

    model = gpt_davinci_model.Davinci()
    story = model.generate_story(keyword_en)

    story_pl = translator.translate(story, dest='pl').text

    return story_pl
