import sentry_sdk

from logging import getLogger

from mathtext.constants import TOKENS2INT_ERROR_INT
from mathtext_fastapi.constants import (
    ERROR_RESPONSE_DICT,
    APPROVED_KEYWORDS,
    APPROVED_INTENTS,
    APPROVED_INTENT_CONFIDENCE_THRESHOLD,
)
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


def evaluate_for_exact_match(normalized_student_message, normalized_expected_answer):
    """Compares the normalized student message and expected answers for a direct match

    >>> evaluate_for_exact_match("2", "2")
    True
    >>> evaluate_for_exact_match("2", "4")
    False
    """
    return normalized_student_message.replace(
        " ", ""
    ) == normalized_expected_answer.replace(" ", "")


def evaluate_for_exact_match_in_phrase(
    normalized_student_message, normalized_expected_answer, expected_answer
):
    """
    evaluate_for_exact_match_in_phrase("2", "2", "2")
    "2"
    >>> evaluate_for_exact_match_in_phrase("yes", "yes", "Yes")
    'Yes'
    >>> evaluate_for_exact_match_in_phrase("I don't know", "4", "4")

    >>> evaluate_for_exact_match_in_phrase("manu", "3", "4")
    'menu'
    """
    tokenized_student_message = normalized_student_message.split()
    return extract_approved_response_from_phrase(
        tokenized_student_message,
        normalized_expected_answer,
        expected_answer,
    )


def check_answer_intent_confidence(intents_results):
    """Checks whether the answer intent is over the approved confidence threshold"""
    is_answer = False

    for result in intents_results.get("intents", []):
        if (
            result.get("data", "") == "math_answer"
            and result.get("confidence", 0.0) >= APPROVED_INTENT_CONFIDENCE_THRESHOLD
        ):
            is_answer = True
    return is_answer


def check_approved_intent_confidence(intents_results):
    """Checks whether approved non-answer intents are over the approved confidence threshold"""
    approved_intent = {}
    for result in intents_results.get("intents", []):
        if (
            result.get("data", "") in APPROVED_INTENTS
            and result.get("confidence", 0) > APPROVED_INTENT_CONFIDENCE_THRESHOLD
        ):
            return build_single_event_nlu_response(
                "intent", result.get("data"), result.get("confidence")
            )
    return approved_intent


def check_nlu_number_result_for_correctness(nlu_eval_result, expected_answer):
    """Check whether an integer or float result is a correct answer or not

    >>> check_nlu_number_result_for_correctness(100, "100")
    {'type': 'correct_answer', 'data': '100', 'confidence': 1.0}
    >>> check_nlu_number_result_for_correctness(None, "20")
    {}
    """
    if nlu_eval_result and nlu_eval_result != None and nlu_eval_result != 0:
        if expected_answer == str(nlu_eval_result):
            label = "correct_answer"
        else:
            label = "wrong_answer"
        return build_single_event_nlu_response(label, str(nlu_eval_result), 1.0)
    return {}


def extract_integers_and_floats_with_regex(message_text, expected_answer):
    """Tries to extract numbers or convert number words to numbers"""
    result = text2float(message_text)
    answer = check_nlu_number_result_for_correctness(result, expected_answer)
    if answer:
        return answer

    result = text2int(message_text)
    answer = check_nlu_number_result_for_correctness(result, expected_answer)
    if answer:
        return answer
    return {}


def check_for_yes_answer_in_intents(intents_results, normalized_expected_answer):
    if normalized_expected_answer == "yes":
        result = next(
            (
                {
                    "data": intent.get("data", ""),
                    "confidence": intent.get("confidence", 0.0),
                }
                for intent in intents_results.get("intents", [])
                if intent.get("data", "") == "yes"
                and intent.get("confidence", 0.0) > APPROVED_INTENT_CONFIDENCE_THRESHOLD
            ),
            None,
        )
        if result:
            return build_single_event_nlu_response(
                "correct_answer",
                result.get("data", "yes"),
                result.get("confidence", 0.0),
            )
    return None


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
            # Evaluation 1 - Check for exact match
            with sentry_sdk.start_span(description="V2 Comparison Evaluation"):
                result = evaluate_for_exact_match(
                    normalized_student_message, normalized_expected_answer
                )
                if result:
                    return build_single_event_nlu_response(
                        "correct_answer", expected_answer, 1.0
                    )

            # Evaluation 2 - Check for pre-defined answers and common misspellings
            with sentry_sdk.start_span(description="V2 Text Evaluation"):
                result = evaluate_for_exact_match_in_phrase(
                    normalized_student_message,
                    normalized_expected_answer,
                    expected_answer,
                )
                if result:
                    if result in APPROVED_KEYWORDS:
                        return build_single_event_nlu_response("keyword", result, 1.0)
                    return build_single_event_nlu_response(
                        "correct_answer", result, 1.0
                    )

            # Evaluation 3 - Check for fraction, decimal, time, and exponent answers
            with sentry_sdk.start_span(description="V2 Regex Number Evaluation"):
                result = run_regex_evaluations(message_text, expected_answer)
                if result:
                    label = "wrong_answer"
                    if result == normalized_expected_answer:
                        label = "correct_answer"
                    return build_single_event_nlu_response(label, result, 1.0)

            # Evaluation 4 - Check for exact int or float number
            with sentry_sdk.start_span(description="V2 Exact Number Evaluation"):
                result = text2num(message_text)
                if result != TOKENS2INT_ERROR_INT:
                    if expected_answer == str(result):
                        return build_single_event_nlu_response(
                            "correct_answer", str(result), 1.0
                        )
                    return build_single_event_nlu_response(
                        "wrong_answer", str(result), 1.0
                    )

        with sentry_sdk.start_span(description="V2 Model Evaluation"):
            # Evaluation 5 - Classify intent with multilabel logistic regression model
            intents_results = predict_message_intent(message_text)

        is_answer = check_answer_intent_confidence(intents_results)

        if is_answer:
            # Evaluation 6 - Extract integers/floats with regex
            with sentry_sdk.start_span(description="V2 Number Extraction"):
                result = extract_integers_and_floats_with_regex(
                    message_text, expected_answer
                )
                if result:
                    return result

        # Evaluation 7 - Extract approved intents
        approved_intent = check_approved_intent_confidence(intents_results)
        if approved_intent:
            return approved_intent

        # Evaluation 8 - Final check for "yes" answer
        yes_intent_as_answer = check_for_yes_answer_in_intents(
            intents_results, normalized_expected_answer
        )
        if yes_intent_as_answer:
            return yes_intent_as_answer

    return build_single_event_nlu_response("out_of_scope", message_text, 0.0)
