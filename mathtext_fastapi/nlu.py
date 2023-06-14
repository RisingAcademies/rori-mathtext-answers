import asyncio
import datetime as dt
import re

from collections.abc import Mapping
from dateutil.parser import isoparse
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from logging import getLogger

from mathtext.text2int import text2int, TOKENS2INT_ERROR_INT
from mathtext.predict_intent import predict_message_intent
# from mathtext_fastapi.cache import get_or_create_redis_entry

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
    return {
        'type': 'integer',
        'data': number_api_resp,
        'confidence': 0
    } 


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
    # Call validate payload
    log.info(f'Starting evaluate message: {message_text}')
    nlu_response = {}
    if len(message_text) < 50:
        # Check the student message for pre-defined keywords
        nlu_response = run_keyword_evaluation(message_text)
        if nlu_response['data']:
            return nlu_response
        
        # Check if the student's message can be converted to a number
        nlu_response = run_text2int_evaluation(
            message_text,
            expected_answer
        )

    if nlu_response.get('data') == TOKENS2INT_ERROR_INT:
        # Run intent classification with logistic regression model
        nlu_response = run_intent_evaluation(message_text)

    return nlu_response
