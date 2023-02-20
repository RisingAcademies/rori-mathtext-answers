import random


def generate_hint(question_nums, right_answer, right_answers, wrong_answers, level, hints_used):
    ord_num = question_nums[1]  # ordinal number
    equation = right_answer - 2 * ord_num - 1
    min_num = equation if equation > 0 else 0
    seq_before = " ".join(
        [str(num) for num in range(right_answer - ord_num, min_num, -ord_num)][::-1]
    )  # sequence before right answer
    seq_after = " ".join(
        [str(num) for num in range(right_answer + ord_num, right_answer + 2 * ord_num + 1, ord_num)]
    )  # sequence after right answer
    hints = [
        f"What number will fill the gap in a sequence {seq_before} ... {seq_after}?",
        f"What number is {ord_num} in the account after {right_answer - ord_num}?",
        f"What number is {ord_num} in the account before {right_answer + ord_num}?",
        f"What number is greater than {right_answer - 1} and less than {right_answer + 1}?"
    ]
    rand_hint = random.choice(hints)
    hints_used += 1

    output = {
        "text": rand_hint,
        "question_numbers": question_nums,
        "right_answer": right_answer,
        'number_correct': right_answers,
        'number_incorrect': wrong_answers,
        'level': level,
        "hints_used": hints_used
    }
    return output