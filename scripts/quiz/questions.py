import random
from typing import Literal


def generate_question_answer_pair(level: Literal["easy", "medium", "hard"] = "easy"):
    """generate question and correct answer to it
    
    :param mode: number we add to current number to get an outcome
    :param current_number: current number we are counting up from
    :param ordinal_number: the number we count up by"""

    numbers = generate_numbers_by_level(level)
    current_number = numbers['current_number']
    ordinal_number = numbers['ordinal_number']
    times = numbers['times']
    proper_outcome = current_number + ordinal_number * times

    question_data = [
        {
            "question": f"Let's practice counting. After {current_number}, what number is next?",
            "current_number": current_number,
            "ordinal_number": ordinal_number,
            "answer": current_number + 1
        },
        {
            "question": f"What number comes {ordinal_number} number after {current_number}?",
            "current_number": current_number,
            "ordinal_number": ordinal_number,
            "answer": current_number + ordinal_number 
        },
        {
            "question": f"We're counting up by {times}s. What number is {ordinal_number} after {current_number}?",
            "current_number": current_number,
            "ordinal_number": ordinal_number,
            "times": times,
            "answer": proper_outcome
        },
        {
            "question": f"If we count up {ordinal_number} from {current_number}, what number is next?",
            "current_number": current_number,
            "ordinal_number": ordinal_number,
            "answer": current_number + ordinal_number
        },
        {
            "question": f"Let's count up by {ordinal_number}s. What number is next if we start from {current_number}",
            "current_number": current_number,
            "ordinal_number": ordinal_number,
            "answer": current_number + ordinal_number
        }
    ]
    random_choice = random.choice(question_data)
    return random_choice


def generate_numbers_by_level(level: Literal["easy", "medium", "hard"] = "easy"):
    """generate current number, ordinal number and times parameter
    
    returns
    dict with params:
    :param current_number: current number
    :param ordinal numebr: the number we count up by
    :param times: the number of times we count up by ordinal number"""

    if level == "easy":
        current_number = random.randint(1, 8)
        ordinal_number = random.randint(1, 2)
        times = 1
    elif level == "medium":
        current_number = random.randint(1, 90)
        ordinal_number = random.randint(1, 5)
        times = random.randint(1, 2)
    elif level == "hard":
        current_number = random.randint(1, 425)
        ordinal_number = random.randint(1, 25)
        times = random.randint(1, 3)

    return {
        "current_number": current_number,
        "ordinal_number": ordinal_number,
        "times": times
    }
