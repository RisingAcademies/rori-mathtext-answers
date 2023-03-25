from typing import Literal

def get_next_level(cur_level, levep_up: Literal[True, False] = True):
    if levep_up:
        if cur_level == "easy":
            return "medium"
        else:
            return "hard"
    else:
        if cur_level == "medium":
            return "easy"
        else:
            return "medium"