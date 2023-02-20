from .questions import generate_question_answer_pair
from .utils import get_next_level


def start_interactive_math(successful_answers=0, wrong_answers=0, level="easy"):
    if wrong_answers > 2:
        wrong_answers = 0
        successful_answers = 0
        level = get_next_level(level, False)
    elif successful_answers > 2:
        successful_answers = 0
        wrong_answers = 0
        level = get_next_level(level)
        
    question_data = generate_question_answer_pair(level)
    question = question_data['question']
    proper_answer = question_data['answer']
    current_number = question_data['current_number']
    ordinal_number = question_data['ordinal_number']

    numbers_group = [current_number, ordinal_number, proper_answer]
    if "times" in question_data:
        times = question_data['times']
        numbers_group.append(times)

    data_to_return = {
        "text": question,
        "question_numbers": numbers_group,
        "right_answer": proper_answer,
        'number_correct': successful_answers,
        'number_incorrect': wrong_answers,
        "hints_used": 0
    }
    return data_to_return

