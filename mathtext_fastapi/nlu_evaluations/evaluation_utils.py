""" These functions perform tasks to help evaluate a message """

from mathtext.utils.extractors import (
    extract_approved_answer_from_phrase,
    extract_approved_keyword_from_phrase,
)
from mathtext_fastapi.constants import (
    APPROVED_INTENT_CONFIDENCE_THRESHOLD,
)


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
    (32202, False)
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

    >>> check_answer_intent_confidence([{'type': 'intent', 'data': 'math_answer', 'confidence': 0.89}])
    True
    >>> check_answer_intent_confidence([{'type': 'intent', 'data': 'math_answer', 'confidence': 0.20}])
    False
    >>> check_answer_intent_confidence([{'type': 'intent', 'data': 'change_topic', 'confidence': 0.89}])
    False
    """
    is_answer = False

    for result in intents_results:
        if (
            result.get("data", "") == "math_answer"
            and result.get("confidence", 0.0) >= APPROVED_INTENT_CONFIDENCE_THRESHOLD
        ):
            is_answer = True
    return is_answer


def check_if_intent_scored_over_approved_confidence_threshold(
    intents_results, target_intent_label
):
    """Determines if the target intent scored above a certain confidence threshold

    >>> check_if_intent_scored_over_approved_confidence_threshold([{'type': 'intent', 'data': 'yes', 'confidence': 0.9936121956268761}], "yes")
    {'data': 'yes', 'confidence': 0.9936121956268761}
    >>> check_if_intent_scored_over_approved_confidence_threshold([{'type': 'intent', 'data': 'yes', 'confidence': 0.0}], "yes")
    {}
    """
    result = next(
        (
            {
                "data": intent.get("data", ""),
                "confidence": intent.get("confidence", 0.0),
            }
            for intent in intents_results
            if intent.get("data", "") == target_intent_label
            and intent.get("confidence", 0.0) > APPROVED_INTENT_CONFIDENCE_THRESHOLD
        ),
        {},
    )
    return result


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
