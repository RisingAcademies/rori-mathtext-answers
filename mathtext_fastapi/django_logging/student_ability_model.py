
def get_bkt_params(activity_session, line_number):
    try:
        params = activity_session.properties["bkt_params"]
        return params["p_learn"], params["p_slip"], params["p_guess"], params["p_transit"]
    except Exception:
        return None, None, None, None

def calculate_lesson_mastery(curr_answer_type, prev_p_learn, p_slip, p_guess, p_transit):
    """
    Calculates the probability of student mastering current lesson based on the most recent answer
    :param curr_answer_type:
    :param prev_p_learn:
    :param p_slip:
    :param p_guess:
    :param p_transit:
    :return: 0 < p_learn <1.0 - the probability of the user mastering the current lesson
    """
    p_learn = prev_p_learn

    if curr_answer_type == "correct_answer":
        cond_p = (prev_p_learn*(1-p_slip))/((prev_p_learn*(1-p_slip)) + (1-prev_p_learn)*p_guess)
    elif curr_answer_type == "wrong_answer":
        cond_p = (prev_p_learn*p_slip)/((prev_p_learn*p_slip) + (1-prev_p_learn)*(1-p_guess))
    else:
        return p_learn

    p_learn = cond_p + (1-cond_p)*p_transit
    return p_learn