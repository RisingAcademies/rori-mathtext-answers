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
from mathtext_fastapi.supabase_logging_async import prepare_message_data_for_logging
# from mathtext_fastapi.supabase_logging import prepare_message_data_for_logging
# from mathtext_fastapi.supabase_logging_psycopg import prepare_message_data_for_logging


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


def check_for_keywords(message_text):
    """ Process a student's message using basic fuzzy text comparison

    >>> check_for_keywords("exit")
    {'type': 'intent', 'data': 'exit', 'confidence': 1.0}
    >>> check_for_keywords("exi")  # doctest: +ELLIPSIS   
    {'type': 'intent', 'data': 'exit', 'confidence': 0...}
    >>> check_for_keywords("eas")  # doctest: +ELLIPSIS
    {'type': 'intent', 'data': 'easy', 'confidence': 0...}
    >>> check_for_keywords("hard")
    {'type': 'intent', 'data': '', 'confidence': 0}
    >>> check_for_keywords("hardier")  # doctest: +ELLIPSIS
    {'type': 'intent', 'data': 'harder', 'confidence': 0...}
    >>> check_for_keywords("I'm tired")  # doctest: +ELLIPSIS
    {'type': 'intent', 'data': 'tired', 'confidence': 1.0}
    """
    label = ''
    ratio = 0
    nlu_response = {'type': 'intent', 'data': label, 'confidence': ratio}
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


def payload_is_valid(payload_object):
    """
    >>> payload_is_valid({'author_id': '+5555555', 'author_type': 'OWNER', 'contact_uuid': '3246-43ad-faf7qw-zsdhg-dgGdg', 'message_body': 'thirty one', 'message_direction': 'inbound', 'message_id': 'SDFGGwafada-DFASHA4aDGA', 'message_inserted_at': '2022-07-05T04:00:34.03352Z', 'message_updated_at': '2023-04-06T10:08:23.745072Z'})
    True

    >>> payload_is_valid({"author_id": "@event.message._vnd.v1.chat.owner", "author_type": "@event.message._vnd.v1.author.type", "contact_uuid": "@event.message._vnd.v1.chat.contact_uuid", "message_body": "@event.message.text.body", "message_direction": "@event.message._vnd.v1.direction", "message_id": "@event.message.id", "message_inserted_at": "@event.message._vnd.v1.chat.inserted_at", "message_updated_at": "@event.message._vnd.v1.chat.updated_at"})
    False
    """
    try:
        isinstance(
            isoparse(payload_object.get('message_inserted_at', '')),
            dt.datetime
        )
        isinstance(
            isoparse(payload_object.get('message_updated_at', '')),
            dt.datetime
        )
    except ValueError:
        return False
    return (
        isinstance(payload_object, Mapping) and
        isinstance(payload_object.get('author_id'), str) and
        isinstance(payload_object.get('author_type'), str) and
        isinstance(payload_object.get('contact_uuid'), str) and
        isinstance(payload_object.get('message_body'), str) and
        isinstance(payload_object.get('message_direction'), str) and
        isinstance(payload_object.get('message_id'), str) and
        isinstance(payload_object.get('message_inserted_at'), str) and
        isinstance(payload_object.get('message_updated_at'), str)
    )


def log_payload_errors(payload_object):
    errors = []
    try:
        assert isinstance(payload_object, Mapping)
    except Exception as e:
        log.error(f'Invalid HTTP request payload object: {e}')
        errors.append(e)
    for k, typ in PAYLOAD_VALUE_TYPES.items():
        try:
            assert isinstance(payload_object.get(k), typ)
        except Exception as e:
            log.error(f'Invalid HTTP request payload object: {e}')
            errors.append(e)
    try:
        assert isinstance(
            dt.datetime.fromisoformat(
                payload_object.get('message_inserted_at')
            ),
            dt.datetime
        )
    except Exception as e:
        log.error(f'Invalid HTTP request payload object: {e}')
        errors.append(e)
    try:
        isinstance(
            dt.datetime.fromisoformat(
                payload_object.get('message_updated_at')
            ),
            dt.datetime
        )
    except Exception as e:
        log.error(f'Invalid HTTP request payload object: {e}')
        errors.append(e)
    return errors


async def evaluate_message_with_nlu(message_data):
    """ Process a student's message using NLU functions and send the result

    # TODO: Update tests with new data structure and coroutine
    evaluate_message_with_nlu({"author_id": "57787919091", "author_type": "OWNER", "contact_uuid": "df78gsdf78df", "message_body": "8", "message_direction": "inbound", "message_id": "dfgha789789ag9ga", "message_inserted_at": "2023-01-10T02:37:28.487319Z", "message_updated_at": "2023-01-10T02:37:28.487319Z"})
    {'type': 'integer', 'data': 8, 'confidence': 0}

    evaluate_message_with_nlu({"author_id": "57787919091", "author_type": "OWNER", "contact_uuid": "df78gsdf78df", "message_body": "I am tired", "message_direction": "inbound", "message_id": "dfgha789789ag9ga", "message_inserted_at": "2023-01-10T02:37:28.487319Z", "message_updated_at": "2023-01-10T02:37:28.487319Z"})  # doctest: +ELLIPSIS
    {'type': 'intent', 'data': 'tired', 'confidence': 1.0}
    """
    # Call validate payload
    log.info(f'Starting evaluate message: {message_data}')

    if not payload_is_valid(message_data):
        log_payload_errors(message_data)
        return {'type': 'error', 'data': TOKENS2INT_ERROR_INT, 'confidence': 0}

    try:
        message_text = str(message_data.get('message_body', ''))
        expected_answer = str(message_data.get('expected_answer', ''))
    except:
        log.error(f'Invalid request payload: {message_data}')
        # use python logging system to do this//
        return {'type': 'error', 'data': TOKENS2INT_ERROR_INT, 'confidence': 0}


    # Check the student message for pre-defined keywords
    intent_api_response = check_for_keywords(message_text)
    if intent_api_response['data']:
        asyncio.create_task(prepare_message_data_for_logging(message_data, intent_api_response))
        # prepare_message_data_for_logging(message_data, nlu_response)
        print("nlu_response")
        print(intent_api_response)
        return intent_api_response

    # Check if the student's message can be converted to a number
    try:
        number_api_resp = text2int(
            message_text.lower(),
            expected_answer
        )
    except ValueError:
        log.error(f'Invalid student message: {message_data}')
        number_api_resp = TOKENS2INT_ERROR_INT

    if number_api_resp == TOKENS2INT_ERROR_INT:
        # Run intent classification with logistic regression model
        nlu_response = predict_message_intent(message_text)
    else:
        nlu_response = build_nlu_response_object(
            'integer',
            number_api_resp,
            0
        )

    asyncio.create_task(prepare_message_data_for_logging(message_data, nlu_response))
    # prepare_message_data_for_logging(message_data, nlu_response)
    print("nlu_response")
    print(nlu_response)
    return nlu_response
