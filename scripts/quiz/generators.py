import random
from .questions import generate_question_data
from .utils import get_next_difficulty, generate_start_step


def start_interactive_math(difficulty=0.01, do_increase: True | False = True):
    next_difficulty = get_next_difficulty(difficulty, do_increase)
    start, step = generate_start_step(difficulty)
    question_data = generate_question_data(start, step, question_num=random.randint(0, 5))

    question = question_data['question']
    start = question_data['start']
    step = question_data['step']

    output = {
        "text": question,
        "difficulty": next_difficulty,
        "question_numbers": [start, step, start + step]
    }
    return output
