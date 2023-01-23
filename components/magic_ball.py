import random


def get_answer_list() -> list[str]:
    answers = [
        'Tak',
        'Nie',
        'Może',
        'Nie wiem',
        'Zapytaj mnie później',
        'Daj mi teraz spokój...',
        'Zdecydowanie tak',
        'Zdecydowanie nie',
        'Raczej tak',
        'Raczej nie',
        'Nie mam zdania'
    ]
    return answers


def get_random_answer():
    answers = get_answer_list()
    return random.choice(answers)
