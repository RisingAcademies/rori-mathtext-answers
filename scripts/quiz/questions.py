from .utils import convert_sequence_to_string


def generate_question_data(start, step, question_num=1):
    """returns question by provided number with filled parameters
    
    parameters
    ----------
    :start: current number
    :step: interval between current and next numbers
    :question_num: question number"""
    seq = convert_sequence_to_string(start, step)
    start_from_num = start + 2 * step
    questions = [
        f"Let's practice counting   {convert_sequence_to_string(start, step, sep='... ')}   After {start_from_num}, what is the next number you will count?\n{seq}",
        f"What number comes {step} number after {start_from_num}?\n{seq}",
        f"We're counting by {step}s.  What number is 1 after {start_from_num}?\n{seq}",
        f"What is {step} number up from {start_from_num}?\n{seq}",
        f"If we count up {step} from {start_from_num}, what number is next?\n{seq}",
    ]
    questions_data = []
    for quest in questions:
        questions_data.append({
            "question": quest,
            "answer": start_from_num + step,
            "start": start_from_num,
            "step": step
        })
    return questions_data[question_num]
