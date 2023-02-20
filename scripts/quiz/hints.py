from random import random


import random

def generate_hint(question_numbers, right_answer, number_correct, number_incorrect, level, hints_used):
    ordinal_number = question_numbers[1]
    equation = right_answer - 2 * ordinal_number - 1
    least_number = equation if equation > 0 else 0
    seq_before_answer = " ".join(
        [str(num) for num in range(right_answer - ordinal_number, least_number, -ordinal_number)][::-1]
    )
    seq_after_answer = " ".join(
        [str(num) for num in range(right_answer + ordinal_number, right_answer + 2 * ordinal_number + 1, ordinal_number)]
    )
    hints = [
        f"What number will fill the gap in a sequence {seq_before_answer} ... {seq_after_answer}?",
        f"What number is {ordinal_number} in the account after {right_answer - ordinal_number}?",
        f"What number is {ordinal_number} in the account before {right_answer + ordinal_number}?",
        f"What number is greater than {right_answer - 1} and less than {right_answer + 1}?"
    ]
    random_hint = random.choice(hints)
    hints_used += 1

    data_to_return = {
        "text": random_hint,
        "question_numbers": question_numbers,
        "right_answer": right_answer,
        'number_correct': number_correct,
        'number_incorrect': number_incorrect,
        'level': level,
        "hints_used": hints_used
    }
    return data_to_return