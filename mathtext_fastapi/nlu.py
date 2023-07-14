import re
import sentry_sdk
import math

from fuzzywuzzy import fuzz, process
from logging import getLogger

from mathtext.constants import TOKENS2INT_ERROR_INT
from mathtext.predict_intent import predict_message_intent
# from mathtext_fastapi.cache import get_or_create_redis_entry
from mathtext.v1_text_processing import format_answer_to_expected_answer_type, format_int_or_float_answer
from mathtext_fastapi.response_formaters import build_single_event_nlu_response, build_evaluation_response_object

log = getLogger(__name__)


# @get_or_create_redis_entry("run_keyword_evaluation")
def run_keyword_evaluation(message_text):
    """ Process a student's message using basic fuzzy text comparison

    >>> run_keyword_evaluation("exit")
    {'type': 'keyword', 'data': 'exit', 'confidence': 1.0}
    >>> run_keyword_evaluation("exi")  # doctest: +ELLIPSIS   
    {'type': 'keyword', 'data': 'exit', 'confidence': 0...}
    >>> run_keyword_evaluation("eas")  # doctest: +ELLIPSIS
    {'type': 'keyword', 'data': 'easy', 'confidence': 0...}
    >>> run_keyword_evaluation("hard")
    {'type': 'keyword', 'data': '', 'confidence': 0}
    >>> run_keyword_evaluation("hardier")  # doctest: +ELLIPSIS
    {'type': 'keyword', 'data': 'harder', 'confidence': 0...}
    >>> run_keyword_evaluation("I'm tired")  # doctest: +ELLIPSIS
    {'type': 'keyword', 'data': 'tired', 'confidence': 1.0}
    """
    label = ''
    ratio = 0
    nlu_response = {
        'type': 'keyword',
        'data': label,
        'confidence': ratio
    }
    keywords = [
        'easier',
        'exit',
        'harder',
        'hint',
        'next',
        'stop',
        'tired',
        'tomorrow',
        'finished',
        'help',
        'easier',
        'easy',
        'support',
        'skip',
        'menu'
    ]

    try:
        tokens = re.findall(r"[-a-zA-Z'_]+", message_text.lower())
    except AttributeError:
        tokens = ''

    for keyword in keywords:
        try:
            tok, score = process.extractOne(keyword, tokens, scorer=fuzz.ratio)
        except:
            score = 0

        if score > 80:
            nlu_response['data'] = keyword
            nlu_response['confidence'] = score / 100

    return nlu_response


# @get_or_create_redis_entry("run_intent_evaluation")
def run_intent_evaluation(message_text):
    nlu_response = predict_message_intent(message_text)
    return nlu_response


async def evaluate_message_with_nlu(message_text, expected_answer):
    """ Process a student's message using NLU functions and send the result

    # TODO: Update tests with new data structure and coroutine
    evaluate_message_with_nlu({"author_id": "57787919091", "author_type": "OWNER", "contact_uuid": "df78gsdf78df", "message_body": "8", "message_direction": "inbound", "message_id": "dfgha789789ag9ga", "message_inserted_at": "2023-01-10T02:37:28.487319Z", "message_updated_at": "2023-01-10T02:37:28.487319Z"})
    {'type': 'integer', 'data': 8, 'confidence': 0}

    evaluate_message_with_nlu({"author_id": "57787919091", "author_type": "OWNER", "contact_uuid": "df78gsdf78df", "message_body": "I am tired", "message_direction": "inbound", "message_id": "dfgha789789ag9ga", "message_inserted_at": "2023-01-10T02:37:28.487319Z", "message_updated_at": "2023-01-10T02:37:28.487319Z"})  # doctest: +ELLIPSIS
    {'type': 'intent', 'data': 'tired', 'confidence': 1.0}
    """
    with sentry_sdk.start_transaction(op="task", name="NLU Evaluation"):
        nlu_responses = {
            'keyword': None,
            'answer_extraction': None,
            'number_extraction': None,
            'intents': None
        }
        # Call validate payload
        log.info(f'Starting evaluate message: {message_text}')
        nlu_response = {}

        # NOTE: If the ',' normalization is removed from the stack
        # ...this will need to be adjusted
        expected_answer = expected_answer.replace(',', '')
        message_text = message_text.replace(',', '')

        if len(message_text) < 50:
            # Check the student message for pre-defined keywords
            
            with sentry_sdk.start_span(description="Comparison Evaluation"):
                normalized_expected_answer = expected_answer.lower()
                normalized_message_text = message_text.lower()
                if normalized_expected_answer.strip() == normalized_message_text.strip():
                    nlu_response = build_single_event_nlu_response(
                        'comparison',
                        expected_answer,
                        1
                    )
                    return nlu_response

            with sentry_sdk.start_span(description="Keyword Evaluation"):
                result = run_keyword_evaluation(message_text)
                if result['data']:
                    nlu_responses['keyword'] = {
                        'result': result['data'],
                        'confidence': result['confidence']
                    }

            # Check if the student's message can be converted to match the expected answer's format
            with sentry_sdk.start_span(description="Text Answer Evaluation"):
                result = format_answer_to_expected_answer_type(message_text, expected_answer)
                if result != TOKENS2INT_ERROR_INT:
                    nlu_responses['answer_extraction'] = {'result': result, 'confidence': 0}

            # Check if the student's message can be converted to a float or int
            with sentry_sdk.start_span(description="Number Evaluation"):
                result = format_int_or_float_answer(message_text)
                if result == math.inf or result == -math.inf:
                    result = TOKENS2INT_ERROR_INT
                if result != TOKENS2INT_ERROR_INT:
                    nlu_responses['number_extraction'] = {'result': result, 'confidence': 0}

        with sentry_sdk.start_span(description="Model Evaluation"):
            # Run intent classification with logistic regression model
            result = run_intent_evaluation(message_text)
            nlu_responses['intents'] = result['intents']

    nlu_response = build_evaluation_response_object(
        nlu_responses,
        evals=['keyword', 'answer_extraction', 'number_extraction', 'intents']
    )

    return nlu_response
