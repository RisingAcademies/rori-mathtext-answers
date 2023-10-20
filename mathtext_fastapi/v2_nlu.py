import sentry_sdk

from logging import getLogger

from mathtext.constants import TOKENS2INT_ERROR_INT
from mathtext_fastapi.constants import (
    APPROVED_INTENT_CONFIDENCE_THRESHOLD,
    APPROVED_INTENTS,
    APPROVED_KEYWORDS,
)
from mathtext.predict_intent import predict_message_intent
from mathtext.utils.nlutils import text2num
from mathtext.utils.text2int_so import text2int, text2float
from mathtext.v2_text_processing import (
    extract_approved_answer_from_phrase,
    extract_approved_keyword_from_phrase,
    normalize_message_and_answer,
    run_regex_evaluations,
    has_profanity,
    is_old_button,
)

# from mathtext_fastapi.cache import get_or_create_redis_entry
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


def evaluate_for_exact_match_with_expected_answer(
    normalized_student_message, normalized_expected_answer
):
    """Compares the normalized student message and expected answers for a direct match

    >>> evaluate_for_exact_match_with_expected_answer("2", "2")
    True
    >>> evaluate_for_exact_match_with_expected_answer("2", "4")
    False
    """
    return normalized_student_message.replace(
        " ", ""
    ) == normalized_expected_answer.replace(" ", "")


def evaluate_for_exact_answer_match_in_phrase(
    normalized_student_message, normalized_expected_answer, expected_answer
):
    """
    evaluate_for_exact_answer_match_in_phrase("2", "2", "2")
    ('2', True)
    >>> evaluate_for_exact_answer_match_in_phrase("yes", "yes", "Yes")
    ('Yes', True)
    >>> evaluate_for_exact_answer_match_in_phrase("I don't know", "4", "4")
    ('32202', False)
    """
    tokenized_student_message = normalized_student_message.split()
    result, is_result_correct = extract_approved_answer_from_phrase(
        tokenized_student_message,
        normalized_expected_answer,
        expected_answer,
    )
    return result, is_result_correct


def evaluate_for_exact_keyword_match_in_phrase(
    normalized_student_message, normalized_expected_answer, expected_answer
):
    """
    >>> evaluate_for_exact_keyword_match_in_phrase("manu", "3", "4")
    'menu'
    """
    tokenized_student_message = normalized_student_message.split()
    result = extract_approved_keyword_from_phrase(
        tokenized_student_message,
        normalized_expected_answer,
        expected_answer,
    )
    return result


def check_answer_intent_confidence(intents_results):
    """Checks whether the answer intent is over the approved confidence threshold

    >>> check_answer_intent_confidence({'intents': [{'type': 'intent', 'data': 'math_answer', 'confidence': 0.89}]})
    True
    >>> check_answer_intent_confidence({'intents': [{'type': 'intent', 'data': 'math_answer', 'confidence': 0.20}]})
    False
    >>> check_answer_intent_confidence({'intents': [{'type': 'intent', 'data': 'change_topic', 'confidence': 0.89}]})
    False
    """
    is_answer = False

    for result in intents_results.get("intents", []):
        if (
            result.get("data", "") == "math_answer"
            and result.get("confidence", 0.0) >= APPROVED_INTENT_CONFIDENCE_THRESHOLD
        ):
            is_answer = True
    return is_answer


def find_highest_confidence_intent_over_threshold(intents_results):
    """Evaluates intent results for the highest confidence intent that is over the approved confidence threshold

    >>> find_highest_confidence_intent_over_threshold([{'type': 'intent', 'data': 'math_answer', 'confidence': 0.89}, {'type': 'intent', 'data': 'change_topic', 'confidence': 0.70}])
    {'type': 'intent', 'data': 'math_answer', 'confidence': 0.89}
    >>> find_highest_confidence_intent_over_threshold([{'type': 'intent', 'data': 'math_answer', 'confidence': 0.20}, {'type': 'intent', 'data': 'change_topic', 'confidence': 0.10}])
    {}
    """
    highest_confidence_intent = {}
    if intents_results:
        highest_confidence_intent = max(intents_results, key=lambda x: x["confidence"])

    if (
        highest_confidence_intent.get("data", "") in APPROVED_INTENTS
        and highest_confidence_intent.get("data", "") != "out_of_scope"
        and highest_confidence_intent.get("confidence", 0)
        > APPROVED_INTENT_CONFIDENCE_THRESHOLD
    ):
        return build_single_event_nlu_response(
            "intent",
            highest_confidence_intent.get("data"),
            highest_confidence_intent.get("confidence"),
        )
    return {}


def check_nlu_number_result_for_correctness(nlu_eval_result, expected_answer):
    """Check whether an integer or float result is a correct answer or not

    >>> check_nlu_number_result_for_correctness(100, "100")
    {'type': 'correct_answer', 'data': '100', 'confidence': 1.0}
    >>> check_nlu_number_result_for_correctness(10, "100")
    {'type': 'wrong_answer', 'data': '10', 'confidence': 1.0}
    >>> check_nlu_number_result_for_correctness(None, "20")
    {}
    """
    label = "wrong_answer"
    if nlu_eval_result and nlu_eval_result not in [None, 0]:
        if expected_answer == str(nlu_eval_result) or are_equivalent_numerical_answers(
            str(nlu_eval_result), expected_answer
        ):
            label = "correct_answer"
            nlu_eval_result = expected_answer
        return build_single_event_nlu_response(label, str(nlu_eval_result))
    return {}


def extract_integers_and_floats_with_regex(student_message, expected_answer):
    """Runs evaluations to extract numbers or convert number words to numbers

    >>> extract_integers_and_floats_with_regex("that's twenty", 20)
    {'type': 'correct_answer', 'data': '20', 'confidence': 1.0}
    >>> extract_integers_and_floats_with_regex("785.12", 20)
    {'type': 'wrong_answer', 'data': '785.12', 'confidence': 1.0}
    >>> extract_integers_and_floats_with_regex("idk", 20)
    {}
    """
    result = text2float(student_message)
    answer = check_nlu_number_result_for_correctness(result, expected_answer)
    if answer and result != TOKENS2INT_ERROR_INT:
        return answer

    result = text2int(student_message)
    answer = check_nlu_number_result_for_correctness(result, expected_answer)
    if answer and result != TOKENS2INT_ERROR_INT:
        return answer
    return {}


def search_through_intent_results(intents_results, target_intent_label):
    """Determines if the target intent scored above a certain confidence threshold

    >>> search_through_intent_results({'intents': [{'type': 'intent', 'data': 'yes', 'confidence': 0.9936121956268761}]}, "yes")
    {'data': 'yes', 'confidence': 0.9936121956268761}
    >>> search_through_intent_results({'intents': [{'type': 'intent', 'data': 'yes', 'confidence': 0.0}]}, "yes")
    {}
    """
    result = next(
        (
            {
                "data": intent.get("data", ""),
                "confidence": intent.get("confidence", 0.0),
            }
            for intent in intents_results.get("intents", [])
            if intent.get("data", "") == target_intent_label
            and intent.get("confidence", 0.0) > APPROVED_INTENT_CONFIDENCE_THRESHOLD
        ),
        {},
    )
    return result


def check_for_yes_answer_in_intents(intents_results, normalized_expected_answer):
    """Check if a yes intent in the expected answer is a correct answer

    >>> check_for_yes_answer_in_intents({'intents': [{'type': 'intent', 'data': 'yes', 'confidence': 0.89}]}, 'yes')
    {'type': 'correct_answer', 'data': 'yes', 'confidence': 0.89}
    >>> check_for_yes_answer_in_intents({'intents': [{'type': 'intent', 'data': 'yes', 'confidence': 0.67}]}, 'no')
    {'type': 'wrong_answer', 'data': 'yes', 'confidence': 0.67}
    >>> check_for_yes_answer_in_intents({'intents': [{'type': 'intent', 'data': 'yes', 'confidence': 0.22}]}, 'yes')
    """
    if normalized_expected_answer in ["yes", "no"]:
        result = search_through_intent_results(intents_results, "yes")

        label = "correct_answer"
        if normalized_expected_answer == "no" and result:
            label = "wrong_answer"

        if result:
            return build_single_event_nlu_response(
                label,
                result.get("data", "yes"),
                result.get("confidence", 0.0),
            )
    return None


def are_equivalent_numerical_answers(str1, str2):
    """Checks whether an integer and float answer are equivalent

    >>> are_equivalent_numerical_answers("17", "17.0")
    True
    >>> are_equivalent_numerical_answers("15.0", "15")
    True
    >>> are_equivalent_numerical_answers("I don't know", "15")
    False
    """
    try:
        num1 = float(str1)
        num2 = float(str2)
        return num1 == num2
    except ValueError:
        return False


def check_for_invalid_input(student_message):
    """Runs evaluations to check if a student message contains inappropriate content for a Q and A conversational turn

    >>> check_for_invalid_input("fuck")
    {'type': 'intent', 'data': 'profanity', 'confidence': 1.0}
    >>> check_for_invalid_input("Continue")
    {'type': 'intent', 'data': 'old_button', 'confidence': 1.0}
    >>> check_for_invalid_input("2")
    {}
    """
    if has_profanity(student_message):
        return build_single_event_nlu_response("intent", "profanity")

    if is_old_button(student_message):
        return build_single_event_nlu_response("intent", "old_button")
    return {}


def extract_number_match_to_expected_answer(
    normalized_student_message, expected_answer
):
    """Runs evaluation to check for decimals or integers in a student message

    >>> extract_number_match_to_expected_answer("6.5", "55.5")
    {'type': 'wrong_answer', 'data': '6.5', 'confidence': 1.0}
    >>> extract_number_match_to_expected_answer("20", "20")
    {'type': 'correct_answer', 'data': '20', 'confidence': 1.0}
    >>> extract_number_match_to_expected_answer("I love math", "100")
    {}
    >>> extract_number_match_to_expected_answer("that's 6", "6")
    {}
    """
    result = text2num(normalized_student_message)

    if result != TOKENS2INT_ERROR_INT:
        if expected_answer == str(result) or are_equivalent_numerical_answers(
            str(result), expected_answer
        ):
            return build_single_event_nlu_response("correct_answer", expected_answer)
        return build_single_event_nlu_response("wrong_answer", str(result))
    return {}


def extract_special_numbers_with_regex(student_message, normalized_expected_answer):
    """Runs evaluation of student message for decimal, fraction, time, and exponent answers

    >>> extract_special_numbers_with_regex("that's 2 / 3", "2/3")
    {'type': 'correct_answer', 'data': '2/3', 'confidence': 1.0}
    >>> extract_special_numbers_with_regex("10: 45 PM", "10:30")
    {'type': 'wrong_answer', 'data': '10:45', 'confidence': 1.0}
    >>> extract_special_numbers_with_regex("idk", "10:30")
    {}
    """
    result = run_regex_evaluations(student_message, normalized_expected_answer)
    if result:
        label = "wrong_answer"
        if result == normalized_expected_answer:
            label = "correct_answer"
        return build_single_event_nlu_response(label, result)
    return {}


def extract_approved_answer(
    normalized_student_message,
    normalized_expected_answer,
    expected_answer,
    student_message,
):
    """Runs evaluation of student message for approved text and numerical expect answers

    >>> extract_approved_answer("yes", "yes", "Yes", "Yes")
    {'type': 'correct_answer', 'data': 'Yes', 'confidence': 1.0}
    >>> extract_approved_answer("b", "a", "B", "A")
    {'type': 'wrong_answer', 'data': 'B', 'confidence': 1.0}
    >>> extract_approved_answer("g", ">", ">", "G")
    {'type': 'correct_answer', 'data': '>', 'confidence': 1.0}
    >>> extract_approved_answer("6", "6", "6", "6")
    {'type': 'correct_answer', 'data': '6', 'confidence': 1.0}
    """
    result, is_result_correct = evaluate_for_exact_answer_match_in_phrase(
        normalized_student_message,
        normalized_expected_answer,
        expected_answer,
    )
    if result and is_result_correct:
        return build_single_event_nlu_response("correct_answer", result)
    if result and result != str(TOKENS2INT_ERROR_INT) and is_result_correct == False:
        intents_results = predict_message_intent(student_message)
        is_answer = check_answer_intent_confidence(intents_results)
        if is_answer:
            return build_single_event_nlu_response(
                "wrong_answer",
                result,
            )
    return {}


def extract_approved_keyword(
    normalized_student_message, normalized_expected_answer, expected_answer
):
    """Runs evaluation to extract an approved keyword from a student message

    >>> extract_approved_keyword('menu', '34', '34')
    {'type': 'keyword', 'data': 'menu', 'confidence': 1.0}
    >>> extract_approved_keyword('menu please', '34', '34')
    {'type': 'keyword', 'data': 'menu', 'confidence': 1.0}
    >>> extract_approved_keyword('34', '34', '34')
    {}
    """
    result = evaluate_for_exact_keyword_match_in_phrase(
        normalized_student_message,
        normalized_expected_answer,
        expected_answer,
    )

    if result and result != str(TOKENS2INT_ERROR_INT):
        if result in APPROVED_KEYWORDS:
            return build_single_event_nlu_response("keyword", result)
    return {}


def extract_exact_match(
    normalized_student_message, normalized_expected_answer, expected_answer
):
    """Runs direct comparison of normalized student message and expected answer

    >>> extract_exact_match("true", "true", "True")
    {'type': 'correct_answer', 'data': 'True', 'confidence': 1.0}
    >>> extract_exact_match("it's 5", "5", "5")
    {}
    >>> extract_exact_match("false", "true", "True")
    {}
    """
    result = evaluate_for_exact_match_with_expected_answer(
        normalized_student_message, normalized_expected_answer
    )
    if result:
        return build_single_event_nlu_response("correct_answer", expected_answer)
    return {}


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
        result = extract_exact_match(
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

        intents_results = None
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
                intents_results = predict_message_intent(student_message)
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
        result = find_highest_confidence_intent_over_threshold(
            intents_results.get("intents", [])
        )
        if result:
            return result

    return build_single_event_nlu_response("out_of_scope", student_message, 0.0)
