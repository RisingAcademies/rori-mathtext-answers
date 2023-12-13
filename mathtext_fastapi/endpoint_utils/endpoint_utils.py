from logging import getLogger

from mathtext_fastapi.django_logging.django_logging import (
    get_user_model,
)
from mathtext_fastapi.django_logging.student_ability_model import (
    get_bkt_params,
    calculate_lesson_mastery,
)
from mathtext_fastapi.v2_nlu import (
    v2_evaluate_message_with_nlu,
)


log = getLogger(__name__)


async def truncate_long_message_text(message_text):
    return message_text[0:100]


async def extract_student_message(message_dict):
    message_text = str(message_dict.get("message_body", ""))
    message_text = await truncate_long_message_text(message_text)
    log.info(f"Message text: {message_text}")
    return message_text


async def extract_student_message_and_expected_answer(message_dict):
    message_text = await extract_student_message(message_dict)
    expected_answer = str(message_dict.get("expected_answer", ""))
    log.info(f"Message text: {message_text}, Expected answer: {expected_answer}")

    return message_text, expected_answer


async def run_nlu_and_activity_evaluation(message_dict):
    message_text, expected_answer = await extract_student_message_and_expected_answer(
        message_dict
    )
    user, user_status, activity, activity_session = await get_user_model(message_dict)

    nlu_response = await v2_evaluate_message_with_nlu(message_text, expected_answer)

    p_learn, p_slip, p_guess, p_transit = get_bkt_params(activity_session)
    if p_learn:
        new_p_learn = calculate_lesson_mastery(
            nlu_response.type, p_slip, p_guess, p_transit
        )
    return nlu_response, activity_session