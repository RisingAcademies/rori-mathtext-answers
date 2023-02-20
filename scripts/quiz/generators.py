from .questions import generate_question_data
from .utils import get_next_level


def start_interactive_math(right_answers=0, wrong_answers=0, level="easy"):
    if wrong_answers > 2:
        wrong_answers = 0
        right_answers = 0
        level = get_next_level(level, False)
    elif right_answers > 2:
        right_answers = 0
        wrong_answers = 0
        level = get_next_level(level)
        
    question_data = generate_question_data(level)
    question = question_data['question']
    right_answer = question_data['answer']
    cur_num = question_data['current_number']
    ord_num = question_data['ordinal_number']
    times = question_data['times']

    numbers_group = [cur_num, ord_num, times]
    output = {
        "text": question,
        "question_numbers": numbers_group,
        "right_answer": right_answer,
        'number_correct': right_answers,
        'number_incorrect': wrong_answers,
        'level': level,
        "hints_used": 0
    }
    return output

