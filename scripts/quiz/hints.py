import random


def generate_hint(start, step, difficulty):
    hints = [
        f"What number is greater than {start} and less than {start + 2 * step}?"
    ]
    hint = random.choice(hints)

    output = {
        "text": hint,
        'difficulty': difficulty,
        "question_numbers": [start, step, start + step]
    }
    return output