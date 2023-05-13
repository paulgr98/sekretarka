import random


def get_answer_list() -> list[str]:
    answers = [
        'Tak',
        'Nie',
        'Może',
        'Nie wiem',
        'Zdecydowanie tak',
        'Zdecydowanie nie',
        'Raczej tak',
        'Raczej nie',
        'Chyba tak',
        'Chyba nie',
        'A czy dzik sra w lesie?',
    ]
    return answers


def get_random_answer():
    answers = get_answer_list()
    return random.choice(answers)
