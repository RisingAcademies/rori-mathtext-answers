

def calculate_lesson_mastery(curr_answer_type, prev_p_learn, p_slip, p_guess, p_transit):

    p_learn = prev_p_learn

    if curr_answer_type == "correct_answer":
        cond_p = (prev_p_learn*(1-p_slip))/((prev_p_learn*(1-p_slip)) + (1-prev_p_learn)*p_guess)
    elif curr_answer_type == "wrong_answer":
        cond_p = (prev_p_learn*p_slip)/((prev_p_learn*p_slip) + (1-prev_p_learn)*(1-p_guess))
    else:
        return p_learn

    p_learn = cond_p + (1-cond_p)*p_transit
    return p_learn