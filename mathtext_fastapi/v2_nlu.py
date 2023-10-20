""" The functions in this file are directly called from the NLU endpoints.  They control the logic of the order of evaluations and send a final response back to the endpoint function """

import sentry_sdk

from logging import getLogger
from mathtext_fastapi.constants import (
    APPROVED_INTENT_CONFIDENCE_THRESHOLD,
)
from mathtext.predict_intent import predict_message_intent
from mathtext.v2_text_processing import (
    normalize_message_and_answer,
    has_profanity,
)
from mathtext_fastapi.nlu_evaluations.evaluations import (
    check_for_invalid_input,
    extract_exact_answer_match,
    extract_approved_answer,
    extract_approved_keyword,
    extract_special_numbers_with_regex,
    extract_integers_and_floats_with_regex,
    check_for_yes_answer_in_intents,
    find_highest_confidence_intent_over_threshold,
    extract_number_match_to_expected_answer,
)
from mathtext_fastapi.nlu_evaluations.evaluation_utils import (
    evaluate_for_exact_keyword_match_in_phrase,
    check_answer_intent_confidence,
)
from mathtext_fastapi.response_formaters import build_single_event_nlu_response

log = getLogger(__name__)


def run_keyword_and_intent_evaluations(text):
    """Evaluates a student message to check the message's intent through an approved keyword or intent

    >>> run_keyword_and_intent_evaluations("fuck")
    {'type': 'intent', 'data': 'profanity', 'confidence': 1.0}
    >>> run_keyword_and_intent_evaluations("menu")
    {'type': 'keyword', 'data': 'menu', 'confidence': 1.0}
    >>> result = run_keyword_and_intent_evaluations("I want to change topics")
    >>> result.get("type", "")
    'intent'
    """
    result = has_profanity(text)
    if result:
        return build_single_event_nlu_response("intent", "profanity")

    result = evaluate_for_exact_keyword_match_in_phrase(text, "", "")
    if result and result != str(32202):
        return build_single_event_nlu_response("keyword", result)
    result = predict_message_intent(text)
    if (
        result
        and result != str(32202)
        and result.get("confidence", 0) > APPROVED_INTENT_CONFIDENCE_THRESHOLD
        and result.get("data") != "out_of_scope"
    ):
        return build_single_event_nlu_response(
            "intent", result.get("data", ""), result.get("confidence", 0)
        )
    return build_single_event_nlu_response("out_of_scope", text, 0.0)


def run_text_processing_evaluations(
    normalized_student_message,
    normalized_expected_answer,
    expected_answer,
    student_message,
):
    # Evaluate 1 - Check for invalid input
    result = check_for_invalid_input(student_message)
    if result:
        return result

    # Evaluation 2 - Check for exact match
    with sentry_sdk.start_span(description="V2 Comparison Evaluation"):
        result = extract_exact_answer_match(
            normalized_student_message,
            normalized_expected_answer,
            expected_answer,
        )
        if result:
            return result

    # Evaluation 3 - Check for pre-defined answers and common misspellings
    with sentry_sdk.start_span(description="V2 Text Evaluation"):
        result = extract_approved_answer(
            normalized_student_message,
            normalized_expected_answer,
            expected_answer,
            student_message,
        )
        if result:
            return result

        result = extract_approved_keyword(
            normalized_student_message,
            normalized_expected_answer,
            expected_answer,
        )
        if result:
            return result

    # Evaluation 4 - Check for fraction, decimal, time, and exponent answers
    with sentry_sdk.start_span(description="V2 Regex Number Evaluation"):
        result = extract_special_numbers_with_regex(
            student_message, normalized_expected_answer
        )
        if result:
            return result

    # Evaluation 5 - Check for exact int or float number
    with sentry_sdk.start_span(description="V2 Exact Number Evaluation"):
        result = extract_number_match_to_expected_answer(
            normalized_student_message, expected_answer
        )
        if result:
            return result
    return {}


async def v2_evaluate_message_with_nlu(student_message, expected_answer):
    """Process a student's message using NLU functions and send the result"""
    with sentry_sdk.start_transaction(op="task", name="V2 NLU Evaluation"):
        log.info(f"Starting evaluate message: {student_message}")

        result = ""
        (
            normalized_student_message,
            normalized_expected_answer,
        ) = normalize_message_and_answer(student_message, expected_answer)

        intents_results = []
        is_answer = None

        if len(student_message) < 50:
            result = run_text_processing_evaluations(
                normalized_student_message,
                normalized_expected_answer,
                expected_answer,
                student_message,
            )
            if result:
                return result

        with sentry_sdk.start_span(description="V2 Model Evaluation"):
            # Evaluation 6 - Classify intent with multilabel logistic regression model
            if not intents_results:
                intents_result_dict = predict_message_intent(student_message)
                intents_results = intents_result_dict.get("intents", [])
                is_answer = check_answer_intent_confidence(intents_results)

        if is_answer:
            # Evaluation 7 - Extract integers/floats with regex
            with sentry_sdk.start_span(description="V2 Number Extraction"):
                result = extract_integers_and_floats_with_regex(
                    student_message, expected_answer
                )
                if result:
                    return result

        # Evaluation 8 - Final check for "yes" answer
        result = check_for_yes_answer_in_intents(
            intents_results, normalized_expected_answer
        )
        if result:
            return result

        # Evaluation 9 - Extract approved intents
        result = find_highest_confidence_intent_over_threshold(intents_results)
        if result:
            return result

    return build_single_event_nlu_response("out_of_scope", student_message, 0.0)
