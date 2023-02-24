import random
from typing import Literal


def generate_question_data(level: Literal["easy", "medium", "hard"] = "easy"):
    """generate question, its numbers and proper answer"""

    nums = generate_numbers_by_level(level)
    cur_num = nums['current_number']  # current number
    ord_num = nums['ordinal_number']  # ordinal number
    seq_up_by_one = generate_number_sequence(cur_num, ord_num=1, times=1)  # sequence with ord_num = 1, times = 1

    count_up_by_one_questions = [
        {
            "question": f"Let's practice counting. After {cur_num}, what number is next?\n{seq_up_by_one}",
            "current_number": cur_num,
            "ordinal_number": 1,
            "times": 1,
            "answer": cur_num + 1
        }
    ]
    seq_up_by_ord = generate_number_sequence(cur_num, ord_num, times=1)  # sequence with times = 1
    count_up_by_ord_questions = [
        {
            "question": f"What number comes {ord_num} number after {cur_num}?\n{seq_up_by_ord}",
            "current_number": cur_num,
            "ordinal_number": ord_num,
            "times": 1,
            "answer": cur_num + ord_num 
        },
        {
            "question": f"If we count up {ord_num} from {cur_num}, what number is next?\n{seq_up_by_ord}",
            "current_number": cur_num,
            "ordinal_number": ord_num,
            "times": 1,
            "answer": cur_num + ord_num
        }
    ]
    times = 1 if level == "easy" else nums['times']
    times_ord_seq = generate_number_sequence(cur_num, ord_num, times)
    times_ord_questions = [
        {
            "question": f"We're counting up by {times}s. What number is {ord_num} after {cur_num}?\n{times_ord_seq}",
            "current_number": cur_num,
            "ordinal_number": ord_num,
            "times": times,
            "answer": cur_num + ord_num * times
        }
    ]
    times_only_seq = generate_number_sequence(cur_num, 1, times)  # sequence with ordinal number = 1
    times_only_questions = [
        {
            "question": f"Let's count up by {times}s. What number is next if we start from {cur_num}?\n{times_only_seq}",
            "current_number": cur_num,
            "ordinal_number": 1,
            "times": times,
            "answer": cur_num + times
        }
    ]
    questions = [*count_up_by_one_questions, *count_up_by_ord_questions, *times_only_questions, *times_ord_questions]
    random_choice = random.choice(questions)
    return random_choice


def generate_numbers_by_level(level: Literal["easy", "medium", "hard"] = "easy"):
    """generate current number, ordinal number and times parameter
    
    returns
    dict with params:
    :param current_number: current number
    :param ordinal numebr: the number we count up by
    :param times: the number of times we count up by ordinal number"""

    if level == "easy":
        cur_num = random.randint(1, 8)
        ord_num = random.randint(1, 2)
        times = 1
    elif level == "medium":
        cur_num = random.randint(1, 94)
        ord_num = random.randint(1, 3)
        times = random.randint(1, 2)
    elif level == "hard":
        cur_num = random.randint(1, 488)
        ord_num = random.randint(1, 4)
        times = random.randint(1, 2)

    return {
        "current_number": cur_num,
        "ordinal_number": ord_num,
        "times": times
    }


def generate_number_sequence(cur_num, ord_num, times=1):
    """generate one of 2 sequences. For example we want 55 to be a right answer, then sequences can be:
    52 53 54 ...
    ... 56 57 58
    
    parameters
    :cur_num: current number
    :ord_num: ordinal number
    :times: times"""
    max_num = cur_num + times * ord_num

    seq_before = [str(num) for num in range(max_num - times, 0, -times)][:3][::-1]
    seq_after = [str(num) for num in range(max_num + times, max_num + 4 * times, times)]
    seq_before.append("...")
    seq_after.insert(0, "...")

    seqs = []
    if len(seq_before) == 4:
        seqs.append(seq_before)
    if len(seq_after) == 4:
        seqs.append(seq_after)
    rand_seq = " ".join(random.choice(seqs))
    return rand_seq
