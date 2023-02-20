from typing import Literal

def get_next_level(current_level, levep_up: Literal[True, False] = True):
    if levep_up:
        if current_level == "easy":
            return "medium"
        else:
            return "hard"
    else:
        if current_level == "medium":
            return "easy"
        else:
            return "medium"