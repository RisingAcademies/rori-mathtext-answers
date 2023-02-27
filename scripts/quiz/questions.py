import random
from typing import Literal


def generate_question_data(level: Literal["easy", "medium", "hard"] = "easy", increment=1):
    """generate question, its numbers and proper answer"""

    nums = generate_numbers_by_level(level)
    cur_num = nums['current_number']                                        # current number
    ord_num = nums['ordinal_number']                                        # ordinal number
    num_seq = generate_number_sequence(cur_num, ord_num, times=increment)   # sequence with ord_num = 1, times = 1

    count_up_by_one_questions = [
        {
            "question": f"Let's practice counting. After {cur_num}, what number is next?\n{num_seq}",
            "current_number": cur_num,
            "ordinal_number": 1,
            "times": 1,
            "answer": cur_num + 1
        }
    ]
    seq_up_by_ord = generate_number_sequence(cur_num, ord_num, times=1)     # sequence with times = 1
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
    times_only_seq = generate_number_sequence(cur_num, 1, times)            # sequence with ordinal number = 1
    times_only_questions = [
        {
            "question": f"Let's count up by {times}s. What number is next if we start from {cur_num}?\n{times_only_seq}",
            "current_number": cur_num,
            "ordinal_number": 1,
            "times": times,
            "answer": cur_num + times
        }
    ]
    print(f"Let's practice counting   {'... '.join([str(num) for num in range(8, 11)])}... After 10, what is the next number you will count?")
    # Let's practice counting   8...  9... 10...   After 10, what is the next number you will count?
    8, 9, 10
    questions = [*count_up_by_one_questions, *count_up_by_ord_questions, *times_only_questions, *times_ord_questions]
    random_choice = random.choice(questions)
    return random_choice


def generate_question(start, step=None, seq=None, question_num=1):
    """returns question by provided number with filled parameters
    
    parameters
    ----------
    :num: question number
    :start: current number
    :step: interval between current and next numbers
    :seq: sequence of numbers"""
    convert_sequence_to_string(start, step, )
    questions = {
        1: f"Let's practice counting   {seq}   After {start}, what is the next number you will count?",
        2: f"What number comes {step} number after {start}?",
        3: f"We're counting by {step}s.  What number is 1 after {start}?",
        4: f"What is {step} number up from {start}?",
        5: f"If we could up {step} from {start}, what number is next?",
    }
    if step > 1:
        questions.update({
            6: f"Now we're counting up by {step} 😄 From {start - 2 * step}, I count {step} numbers to get to {start - step}.  Then from {start - step} I count {step} numbers to get to {start}.  What is {step} numbers after {start}?",
            7: f"What is {step} numbers after {start}?  Let's count one number ... {start + 1}... now what is the next number?"
        })
    return questions[question_num]


def generate_start_by_score(score):
    """generate number by scrore
    
    to calculate the starting point """
    if score <= 0.3:
        range_size = 27 - 1                              # total range size
        range_offset = score                             # offset from the lower end of the range
        proportion = range_offset / 0.3                  # proportion of the total range
        number_range = int(proportion * range_size)      # size of the range based on the argument
        return random.randint(1, 1 + number_range)
    elif score >= 0.6:
        range_size = 495 - 97                            # total range size
        range_offset = score - 0.6                       # offset from the lower end of the range
        proportion = range_offset / (1 - 0.6)            # proportion of the total range
        number_range = int(proportion * range_size)      # size of the range based on the argument
        return random.randint(98, 98 + number_range)
    else:
        range_size = 97 - 28                             # total range size
        range_offset = score - 0.3                       # offset from the lower end of the range
        proportion = range_offset / (0.6 - 0.3)          # proportion of the total range
        number_range = int(proportion * range_size)      # size of the range based on the argument
        return random.randint(28, 28 + number_range)


def convert_sequence_to_string(start, step):
    func_vars = {}
    exec("seq = ', '.join([str(num) for num in range({start}, {stop}, {step})][::-1])".format(start=start, stop=start-3*step, step=step * (-1)), func_vars)
    return func_vars['seq']



def generate_numbers_by_level(level: Literal["easy", "medium", "hard"] = "easy"):
    """generate current number, ordinal number and times parameter
    
    returns
    dict with params:
    :param current_number: current number
    :param ordinal numebr: the number we count up by
    :param times: the number of times we count up by ordinal number"""

    if level == "easy":
        cur_num = random.randint(5, 15)
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
