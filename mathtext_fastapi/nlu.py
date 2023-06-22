import asyncio
import datetime as dt
import re
import sentry_sdk
import math

from collections.abc import Mapping
from dateutil.parser import isoparse
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from logging import getLogger

from mathtext.text2int import text2int, TOKENS2INT_ERROR_INT
from mathtext.predict_intent import predict_message_intent
# from mathtext_fastapi.cache import get_or_create_redis_entry
from mathtext.text2int import format_answer_to_expected_answer_type, format_int_or_float_answer


log = getLogger(__name__)

PAYLOAD_VALUE_TYPES = {
    'author_id': str,
    'author_type': str,
    'contact_uuid': str,
    'message_body': str,
    'message_direction': str,
    'message_id': str,
    'message_inserted_at': str,
    'message_updated_at': str,
    }


def build_nlu_response_object(nlu_type, data, confidence):
    """ Turns nlu results into an object to send back to Turn.io
    Inputs
    - nlu_type: str - the type of nlu run (integer or intent)
    - data: str/int - the student message
    - confidence: - the nlu confidence score (intent) or '' (integer)

    >>> build_nlu_response_object('integer', 8, 0)
    {'type': 'integer', 'data': 8, 'confidence': 0}
    """
    return {
        'type': nlu_type,
        'data': data,
        'confidence': confidence
        }

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


# @get_or_create_redis_entry("run_text2int_evaluation")
def run_text2int_evaluation(message_text, expected_answer):
    try:
        number_api_resp = text2int(
            message_text.lower(),
            expected_answer
        )
    except ValueError:
        log.error(f'Invalid student message: {message_text}')
        number_api_resp = TOKENS2INT_ERROR_INT

    if number_api_resp == math.inf or number_api_resp == -math.inf:
        number_api_resp = TOKENS2INT_ERROR_INT

    return {
        'type': 'integer',
        'data': number_api_resp,
        'confidence': 0
    } 


# @get_or_create_redis_entry("run_intent_evaluation")
def run_intent_evaluation(message_text):
    nlu_response = predict_message_intent(message_text)
    return nlu_response


def format_nlu_response(eval_type, result, confidence=0, intents=None):
    """ Formats the result of an evaluation or error to the format Rori expects
    
    >>> format_nlu_response('answer_extraction', 'Yes')
    {'type': 'answer_extraction', 'data': 'Yes', 'confidence': 0, 'intents': [], 'extracted_answer': [], 'numerical_answer': []}
    """
    result_obj = {
        'type': eval_type,
        'data': result,
        'confidence': confidence,
    }
    result_list = []
    if eval_type == 'timeout' or eval_type == 'error':
        result_list = [
            result_obj.copy() for i in range(3)
        ]
    
    nlu_response = {
        'type': eval_type,
        'data': result,
        'confidence': confidence,
        'intents': result_list,
        'extracted_answer': [],
        'numerical_answer': []
    }
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
        # Call validate payload
        log.info(f'Starting evaluate message: {message_text}')
        nlu_response = {}

        if len(message_text) < 50:
            # Check the student message for pre-defined keywords
        
            with sentry_sdk.start_span(description="Comparison Evaluation"):
                if expected_answer.lower().strip() == message_text.lower().strip():
                    nlu_response = format_nlu_response(
                        'comparison',
                        expected_answer,
                        1
                    )
                    return nlu_response

            with sentry_sdk.start_span(description="Keyword Evaluation"):
                result = run_keyword_evaluation(message_text)
                if result['data']:
                    nlu_response = format_nlu_response(
                        'keyword',
                        result['data'],
                        result['confidence']
                    )
                    return nlu_response

            # Check if the student's message can be converted to match the expected answer's format
            with sentry_sdk.start_span(description="Text Answer Evaluation"):
                result = format_answer_to_expected_answer_type(message_text, expected_answer)
                if result != TOKENS2INT_ERROR_INT:
                    nlu_response = format_nlu_response('answer_extraction', result)
                    return nlu_response

            # Check if the student's message can be converted to a float or int
            with sentry_sdk.start_span(description="Number Evaluation"):
                result = format_int_or_float_answer(message_text)
                if result != TOKENS2INT_ERROR_INT:
                    nlu_response = format_nlu_response('number_extraction', result)
                    return nlu_response

        with sentry_sdk.start_span(description="Model Evaluation"):
            if nlu_response == TOKENS2INT_ERROR_INT:
                # Run intent classification with logistic regression model
                nlu_response = run_intent_evaluation(message_text)
    return nlu_response
