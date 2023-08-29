import sentry_sdk

from logging import getLogger

from mathtext.constants import TOKENS2INT_ERROR_INT
from mathtext_fastapi.constants import ERROR_RESPONSE_DICT
from mathtext.predict_intent import predict_message_intent

from mathtext.utils.nlutils import text2num
from mathtext.utils.text2int_so import text2int, text2float
from mathtext.v2_text_processing import (
    normalize_message_and_answer,
    extract_approved_response_from_phrase,
    run_regex_evaluations,
)

# from mathtext_fastapi.cache import get_or_create_redis_entry
from mathtext_fastapi.response_formaters import build_single_event_nlu_response

log = getLogger(__name__)


async def v2_evaluate_message_with_nlu(message_text, expected_answer):
    """Process a student's message using NLU functions and send the result"""
    with sentry_sdk.start_transaction(op="task", name="V2 NLU Evaluation"):
        log.info(f"Starting evaluate message: {message_text}")

        result = ""
        (
            normalized_student_message,
            normalized_expected_answer,
        ) = normalize_message_and_answer(message_text, expected_answer)

        if len(message_text) < 50:
            with sentry_sdk.start_span(description="V2 Comparison Evaluation"):
                if normalized_student_message.replace(
                    " ", ""
                ) == normalized_expected_answer.replace(" ", ""):
                    return build_single_event_nlu_response(
                        "correct_answer", expected_answer, 1.0
                    )

            # Check for pre-defined answers and common misspellings
            with sentry_sdk.start_span(description="V2 Text Evaluation"):
                tokenized_student_message = normalized_student_message.split()
                result = extract_approved_response_from_phrase(
                    tokenized_student_message,
                    normalized_expected_answer,
                    expected_answer,
                )
                if result:
                    if result in [
                        "easier",
                        "exit",
                        "harder",
                        "hint",
                        "next",
                        "stop",
                        "tired",
                        "tomorrow",
                        "finished",
                        "help",
                        "easier",
                        "easy",
                        "support",
                        "skip",
                        "menu",
                    ]:
                        return build_single_event_nlu_response("keyword", result, 1.0)
                    return build_single_event_nlu_response(
                        "correct_answer", result, 1.0
                    )

            # Check for fraction, decimal, time, and exponent answers
            with sentry_sdk.start_span(description="V2 Regex Number Evaluation"):
                result = run_regex_evaluations(message_text, expected_answer)
                if result:
                    return build_single_event_nlu_response(
                        "correct_answer", result, 1.0
                    )

            # Check for exact int or float number
            with sentry_sdk.start_span(description="V2 Exact Number Evaluation"):
                result = text2num(message_text)
                if result != TOKENS2INT_ERROR_INT:
                    if expected_answer == str(result):
                        return build_single_event_nlu_response(
                            "correct_answer", result, 0
                        )
                    return build_single_event_nlu_response("wrong_answer", result, 0)

        with sentry_sdk.start_span(description="V2 Model Evaluation"):
            # Classify intent with multilabel logistic regression model
            result = predict_message_intent(message_text)

        is_answer = False
        try:
            for result in result.get("intents", []):
                if (
                    result.get("data", "") == "answer"
                    and result.get("confidence", 0) >= 0.8
                ):
                    is_answer = True
        except:
            return ERROR_RESPONSE_DICT

        if is_answer:
            # Extract integers/floats with regex
            with sentry_sdk.start_span(description="V2 Number Extraction"):
                label = "wrong_answer"
                result = text2float(message_text)
                if result and result != None:
                    if expected_answer == str(result):
                        label = "correct_answer"
                    return build_single_event_nlu_response(label, result, 0)

                result = text2int(message_text)
                if result and result != 0:
                    if expected_answer == str(result):
                        label = "correct_answer"
                    return build_single_event_nlu_response(label, result, 0)

    return build_single_event_nlu_response("out_of_scope", message_text, 0)
