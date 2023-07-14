import sentry_sdk

from logging import getLogger

from mathtext.constants import TOKENS2INT_ERROR_INT
from mathtext.predict_intent import predict_message_intent
from mathtext.v1_text_processing import format_int_or_float_answer
from mathtext.v2_text_processing import normalize_message_and_answer, extract_approved_response_from_phrase, run_regex_evaluations
# from mathtext_fastapi.cache import get_or_create_redis_entry
from mathtext_fastapi.response_formaters import build_single_event_nlu_response, build_evaluation_response_object

log = getLogger(__name__)


async def v2_evaluate_message_with_nlu(message_text, expected_answer):
    """ Process a student's message using NLU functions and send the result

    # TODO: Update tests with new data structure and coroutine
    evaluate_message_with_nlu({"author_id": "57787919091", "author_type": "OWNER", "contact_uuid": "df78gsdf78df", "message_body": "8", "message_direction": "inbound", "message_id": "dfgha789789ag9ga", "message_inserted_at": "2023-01-10T02:37:28.487319Z", "message_updated_at": "2023-01-10T02:37:28.487319Z"})
    {'type': 'integer', 'data': 8, 'confidence': 0}

    evaluate_message_with_nlu({"author_id": "57787919091", "author_type": "OWNER", "contact_uuid": "df78gsdf78df", "message_body": "I am tired", "message_direction": "inbound", "message_id": "dfgha789789ag9ga", "message_inserted_at": "2023-01-10T02:37:28.487319Z", "message_updated_at": "2023-01-10T02:37:28.487319Z"})  # doctest: +ELLIPSIS
    {'type': 'intent', 'data': 'tired', 'confidence': 1.0}
    """
    with sentry_sdk.start_transaction(op="task", name="V2 NLU Evaluation"):
        log.info(f'Starting evaluate message: {message_text}')

        result = ''
        normalized_student_message, normalized_expected_answer= normalize_message_and_answer(message_text, expected_answer)

        nlu_responses = {
            'text_extraction': None,
            'regex_answer_extraction': None,
            'number_extraction': None,
            'intents': None
        }

        if len(message_text) < 50:
            with sentry_sdk.start_span(description="V2 Comparison Evaluation"):
                if normalized_student_message.replace(' ', '') == normalized_expected_answer.replace(' ', ''):
                    return build_single_event_nlu_response(
                        'comparison',
                        expected_answer
                    )

            # Check for pre-defined answers and common misspellings
            with sentry_sdk.start_span(description="V2 Text Evaluation"):
                tokenized_student_message = normalized_student_message.split()
                result = extract_approved_response_from_phrase(
                    tokenized_student_message,
                    normalized_expected_answer,
                    expected_answer
                )
                if result:
                    nlu_responses['text_extraction'] = {'result': result, 'confidence': 1}

            # Check for fraction, decimal, time, and exponent answers
            with sentry_sdk.start_span(description="V2 Regex Number Evaluation"):
                result = run_regex_evaluations(message_text, expected_answer)
                if result:
                    nlu_responses['regex_answer_extraction'] = {'result': result, 'confidence': 0}

            # Extract integers/floats with regex
            with sentry_sdk.start_span(description="V2 Number Misspelling Evaluation"):
                result = format_int_or_float_answer(message_text)
                if result != TOKENS2INT_ERROR_INT and result:
                    nlu_responses['number_extraction'] = {'result': str(result), 'confidence': 0 }

        with sentry_sdk.start_span(description="V2 Model Evaluation"):
            # Run intent classification with logistic regression model
            result = predict_message_intent(message_text)
            nlu_responses['intents'] = result['intents']

    nlu_response = build_evaluation_response_object(nlu_responses)

    return nlu_response
