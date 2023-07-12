import sentry_sdk

from logging import getLogger

from mathtext.constants import TOKENS2INT_ERROR_INT
from mathtext.predict_intent import predict_message_intent
from mathtext.v1_text_processing import format_int_or_float_answer
from mathtext.v2_text_processing import normalize_message_and_answer, extract_approved_response_from_phrase, run_regex_evaluations
# from mathtext_fastapi.cache import get_or_create_redis_entry

log = getLogger(__name__)


def format_single_event_nlu_response(
    eval_type,
    result,
    confidence=1,
    intents=[]
):
    """ Formats the result of a single event to the standard nlu response format

    Currently applies to comparison evaluation, timeout, and error responses
    
    >>> format_single_event_nlu_response('comparison', '25')
    {'type': 'comparison', 'data': '25', 'confidence': 1, 'intents': [{'type': 'comparison', 'data': '25', 'confidence': 1}, {'type': 'comparison', 'data': '25', 'confidence': 1}, {'type': 'comparison', 'data': '25', 'confidence': 1}]}
    """
    result_obj = {
        'type': eval_type,
        'data': result,
        'confidence': confidence,
    }

    intents = [
        result_obj.copy() for i in range(3)
    ]
    
    nlu_response = {
        'type': eval_type,
        'data': result,
        'confidence': confidence,
        'intents': intents,
    }
    return nlu_response


def build_evaluation_response_object(results):
    """ Builds a response that based on the outcome of all the evaluations 
    
    # TODO: Update test
    build_evaluation_response_object({'keyword': None, 'answer_extraction': 'Yes', 'numerical_extraction': None, 'intents': {'data': 'yes', 'confidence': 0.7285137685012592, 'intents': [{'type': 'intent', 'data': 'yes', 'confidence': 0.7285137685012592}, {'type': 'intent', 'data': 'next_lesson', 'confidence': 0.43764260237929115}, {'type': 'intent', 'data': 'spam', 'confidence': 0.39586822881508865}]}})
    {'type': 'answer_extraction', 'data': 'Yes', 'confidence': 0, 'intents': [{'type': 'intent', 'data': 'yes', 'confidence': 0.7285137685012592}, {'type': 'intent', 'data': 'next_lesson', 'confidence': 0.43764260237929115}, {'type': 'intent', 'data': 'spam', 'confidence': 0.39586822881508865}]}
    """
    nlu_response = {
        'type': '',
        'data': '',
        'confidence': 0,
        'intents': results.get('intents', []).get('intents', '')
    }

    if results.get('text_extraction', ''):
        nlu_response['type'] = 'text_extraction'
        nlu_response['data'] = results.get('text_extraction', '')
    elif results.get('regex_answer_extraction', ''):
        nlu_response['type'] = 'regex_answer_extraction'
        nlu_response['data'] = results.get('regex_answer_extraction', '')
    elif results.get('number_extraction', ''):
        nlu_response['type'] = 'number_extraction'
        nlu_response['data'] = results.get('number_extraction', '')
    else:
        nlu_response['type'] = 'intent'
        try:
            nlu_response['data'] = results['intents']['intents'][0]['data']
            nlu_response['confidence'] = results['intents']['intents'][0]['confidence']
        except:
            nlu_response['data'] = TOKENS2INT_ERROR_INT
            nlu_response['confidence'] = 0
    
    return nlu_response


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
                    return format_single_event_nlu_response(
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
                    nlu_responses['text_extraction'] = result

            # Check for fraction, decimal, time, and exponent answers
            with sentry_sdk.start_span(description="V2 Regex Number Evaluation"):
                result = run_regex_evaluations(message_text, expected_answer)
                if result:
                    nlu_responses['regex_answer_extraction'] = result

            # Extract integers/floats with regex
            with sentry_sdk.start_span(description="V2 Number Misspelling Evaluation"):
                result = format_int_or_float_answer(message_text)
                if result != TOKENS2INT_ERROR_INT and result:
                    nlu_responses['number_extraction'] = str(result)

        with sentry_sdk.start_span(description="V2 Model Evaluation"):
            # Run intent classification with logistic regression model
            result = predict_message_intent(message_text)
            nlu_responses['intents'] = {
                'data': result['data'],
                'confidence': result['confidence'],
                'intents': result['intents']
            }

    nlu_response = build_evaluation_response_object(nlu_responses)

    return nlu_response
