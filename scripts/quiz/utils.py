import pandas
import random
from scipy.interpolate import interp1d
from typing import Literal

def get_next_difficulty(difficulty, do_increase: Literal[True, False] = True):
    if do_increase:
        if difficulty >= 0.95:
            next_difficulty = round(random.uniform(0.95, 0.99), 2)
        else:
            next_difficulty = round(random.uniform(difficulty + 0.01, difficulty + 0.05), 2)
    else:
        if difficulty <= 0.05:
            next_difficulty = round(random.uniform(0.01, 0.05), 2)
        else:
            next_difficulty = round(random.uniform(difficulty - 0.05, difficulty - 0.01), 2)

    return next_difficulty


def generate_start_step(difficulty: float, path_to_csv_file: str = "scripts/quiz/data.csv"):
    """generate start and step values interpolating results to function built from data from file"""
    df = pandas.read_csv(path_to_csv_file, delimiter=',', header=0, names=['difficulty', 'start'])
    all_rows = df.loc[:]

    difficulties = [row_data['difficulty'] for _, row_data in all_rows.iterrows()]
    starts = [row_data['start'] for _, row_data in all_rows.iterrows()]

    interp_start_func = interp1d(difficulties, starts)
    generated_start = round(float(interp_start_func(difficulty)))
    if difficulty <= 0.3:
        step = 1
    elif difficulty > 0.6:
        step = 10
    else:
        step = 5
    return (generated_start, step)


def convert_sequence_to_string(start, step, sep=", "):
    stop = start + 3 * step
    return sep.join([str(num) for num in range(start, stop, step)]) + sep