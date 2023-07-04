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

import copy
import datetime
import pandas as pd
import re

log = getLogger(__name__)

# Only used for simulated_evaluation function
KEYWORDS = [
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
    'easy',
    'support',
    'skip',
    'menu'
]


APPROVED_RESPONSE_CASES = [
    ['yes', 'answer', ['yes', 't']],
    ['y', 'answer', ['yes', 't']],
    ['yah', 'answer', ['yes', 't']],
    ['yeah', 'answer', ['yes',  't']],
    ['ok', 'answer', ['yes', 't']],
    ['okay', 'answer', ['yes', 't']],
    ['okey', 'answer', ['yes', 't']],
    ['yea', 'answer', ['yes', 't']],
    ['yh', 'answer', ['yes', 't']],
    ['ys', 'answer', ['yes', 't']],
    ['yrs', 'answer', ['yes', 't']],
    ['yes.', 'answer', ['yes', 't']],
    ['yep', 'answer', ['yes', 't']],
    ['yee', 'answer', ['yes', 't']],
    ['yed', 'answer', ['yes', 't']],
    ['yesh', 'answer', ['yes', 't']],
    ['yew', 'answer', ['yes', 't']],
    ['yex', 'answer', ['yes', 't']],
    ['yey', 'answer', ['yes', 't']],
    ['yez', 'answer', ['yes', 't']],
    ['ready', 'answer', ['yes']],
    ['proceed', 'answer', ['yes']],
    ['continue', 'answer', ['yes']],
    ['t', 'answer', ['yes', 't']],
    ['true', 'answer', ['yes', 't']],
    ['1', 'answer', ['yes', 't']],
    ['no', 'answer', ['no', 'f']],
    ['n', 'answer', ['no', 'f']],
    ['nah', 'answer', ['no', 'f']],
    ['f', 'answer', ['no', 'f']],
    ['false', 'answer', ['no', 'f']],
    ['0', 'answer', ['no', 'f']],
    ['even', 'answer', ['even']],
    ['odd', 'answer', ['odd']],
    ['monday', 'answer', ['monday']],
    ['tuesday', 'answer', ['tuesday']],
    ['wednesday', 'answer', ['wednesday']],
    ['thursday', 'answer', ['thursday']],
    ['friday', 'answer', ['friday']],
    ['saturday', 'answer', ['saturday']],
    ['sunday', 'answer', ['sunday']],
    ['mon', 'answer', ['monday']],
    ['tues', 'answer', ['tuesday']],
    ['wed', 'answer', ['wednesday']],
    ['thurs', 'answer', ['thursday']],
    ['fri', 'answer', ['friday']],
    ['sat', 'answer', ['saturday']],
    ['sun', 'answer', ['sunday']],
    ['>', 'answer', ['>', 'g']],
    ['g', 'answer', ['>', 'g']],
    ['gt', 'answer', ['>', 'g']],
    ['greater', 'answer', ['>', 'g']],
    ['greater than', 'answer', ['>', 'g']],
    ['<', 'answer', ['<', 'l']],
    ['l', 'answer', ['<', 'l']],
    ['lt', 'answer', ['<', 'l']],
    ['less', 'answer', ['<', 'l']],
    ['less than', 'answer', ['<', 'l']],
    ['>=', 'answer', ['>=', 'gte']],
    ['gte', 'answer', ['>=', 'gte']],
    ['greater than or equal', 'answer', ['>=', 'gte']],
    ['<=', 'answer', ['<=', 'lte']],
    ['lte', 'answer', ['<=', 'lte']],
    ['less than or equal', 'answer', ['<=', 'lte']],
    ['=', 'answer', ['=', 'e']],
    ['e', 'answer', ['=', 'e']],
    ['equal', 'answer', ['=', 'e']],
    ['same', 'answer', ['=', 'e']],
    ['a', 'answer', ['a']],
    ['b', 'answer', ['b']],
    ['c', 'answer', ['c']],
    ['d', 'answer', ['d']],
    ['easier', 'keyword', 'easier'],
    ['harder', 'keyword', 'harder'],
    ['hint', 'keyword', 'hint'],
    ['next', 'keyword', 'next'],
    ['stop', 'keyword', 'stop'],
    ['help', 'keyword', 'help'],
    ['support', 'keyword', 'support'],
    ['skip', 'keyword', 'skip'],
    ['menu', 'keyword', 'menu'],
    # These keywords below may not be very useful
    ['finish', 'keyword', 'finish'],
    ['hard', 'keyword', 'hard'],
    ['tired', 'keyword', 'tired'],
    ['tomorrow', 'keyword', 'tomorrow'],
    ['finished', 'keyword', 'finished'],
    ['exit', 'keyword', 'exit'],
    ['easy', 'keyword', 'easy'],
    ['manu', 'keyword', 'menu'],
    ['menue', 'keyword', 'menu'],
    ['meun', 'keyword', 'menu'],
    ['menus', 'keyword', 'menu'],
    ['skip', 'keyword', 'menu'],
    ['hints', 'keyword', 'menu']
]

APPROVED_RESPONSES_BY_TYPE = {}
KEYWORD_LOOKUP = {}
TEXT_ANSWER_LOOKUP = {}
for entry in APPROVED_RESPONSE_CASES:
    APPROVED_RESPONSES_BY_TYPE[entry[0]] = entry[1]
    if entry[1] == 'answer':
        TEXT_ANSWER_LOOKUP[entry[0]] = entry[2]
    else:
        KEYWORD_LOOKUP[entry[0]] = entry[2]

NUMBER_MAP = {
    'one': 1,
    'two': 2,
    'three': 3,
    'four': 4,
    'five': 5,
    'six': 6,
    'seven': 7,
    'eight': 8,
    'nine': 9,
    'ten': 10,
    'eleven': 11,
    'twelve': 12,
    'thirteen': 13,
    'fourteen': 14,
    'fifteen': 15,
    'sixteen': 16,
    'seventeen': 17,
    'eighteen': 18,
    'nineteen': 19,
    'twenty': 20,
    'thirty': 30,
    'forty': 40,
    'fourty': 40,
    'fifty': 50,
    'sixty': 60,
    'seventy': 70,
    'eighty': 80,
    'ninety': 90,
    'hundred': 100,
    'thousand': 1000,
    'million': 1000000,
    'billion': 1000000000,
    'trillion': 1000000000000,
}


def regex_evaluation(normalized_student_message):
    """
    >>> regex_evaluation("it's 11:30")
    '11:30'
    >>> regex_evaluation('maybe 1/2')
    '1/2'
    """
    try:
        timestamp = datetime.datetime.strptime(normalized_student_message[3:-1], '%H:%M:%S')
        text = timestamp.strftime('%H:%M')
    except ValueError:
        text = normalized_student_message
    patterns = [
        r'\b\d{1,2}\s*:\s*\d{2}\b', # time
        r'[-]?\d+(\.\d+)?\s*\^\s*[-]?\d+(\.\d+)?', # exponent
        r'(\d+\s+)?\d+\s*/\s*\d+', # fraction
        r"\d+\s*?\.\s*?\d+" # decimal
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            normalized_response = re.sub(r'\s', "", match.group(0))
            return normalized_response


def normalize_message_and_answer(student_message, expected_answer):
    """
    >>> normalize_message_and_answer("Maybe 5000", "5,000")
    ('maybe 5000', '5000')
    >>> normalize_message_and_answer("Yeah I think so", "Yes")
    ('yeah i think so', 'yes')
    """
    normalized_student_message = str(student_message).strip().replace(',','').lower()[0:100] 
    normalized_expected_answer = str(expected_answer).strip().replace(',','').lower()
    return normalized_student_message, normalized_expected_answer


def extract_approved_response_from_phrase(
    tokenized_student_message,
    normalized_expected_answer,
    expected_answer
):
    """
    >>> extract_approved_response_from_phrase(['maybe', 'y'], 'yes', 'Yes')   
    'Yes'
    >>> extract_approved_response_from_phrase(['*menu*', 'y'], 'yes', 'Yes')   
    'Yes'
    >>> extract_approved_response_from_phrase(['maybe', '5000'], '5000', '5000')   
    '5000'
    """
    answer_dict = copy.deepcopy(APPROVED_RESPONSES_BY_TYPE)
    if not answer_dict.get(normalized_expected_answer,''):
        answer_dict[normalized_expected_answer] = 'expected_answer'
    answer_types = [(answer_dict[token.replace('.', '').replace('*','')], token.replace('.', '').replace('*','')) for token in tokenized_student_message if token.replace('.', '').replace('*','') in answer_dict]

    for answer_type in answer_types:
        if answer_type[0] == 'expected_answer':
            return expected_answer
    for answer_type in answer_types:
        if answer_type[0] == 'answer' and normalized_expected_answer in TEXT_ANSWER_LOOKUP[answer_type[1]]:
            return expected_answer
    for answer_type in answer_types:
        if answer_type[0] == 'keyword':
            return KEYWORD_LOOKUP[answer_type[1]]


def is_number(normalized_student_message):
    """
    >>> is_number("maybe 5000")
    False
    >>> is_number("2")
    True
    >>> is_number("2.75")
    True
    >>> is_number("-3")
    True
    """
    try:
        if float(normalized_student_message):
            return True
    except ValueError:
        pass
    try:
        if int(normalized_student_message):
            return True
    except ValueError:
        pass
    return False


def extract_numbers_with_regex(
    normalized_student_message,
    normalized_expected_answer,
    expected_answer
):
    """
    >>> extract_numbers_with_regex("maybe 5000", "5000", "5,000")
    '5,000'
    >>> extract_numbers_with_regex("maybe it's 2.5 or 3.5", "5", "5")
    
    >>> extract_numbers_with_regex("maybe", "5", "5")
    
    """
    result = re.search(r"\d+(?:\.\d+)?|\d", normalized_student_message)  
    is_num_expected_answer = is_number(normalized_expected_answer)
    if is_num_expected_answer and result:
        if result[0] == normalized_expected_answer:
            return expected_answer


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

# @get_or_create_redis_entry("v2_run_keyword_evaluation")
def v2_run_keyword_evaluation(message_text):
    """ Process a student's message using basic fuzzy text comparison

    >>> v2_run_keyword_evaluation("exit")
    {'type': 'keyword', 'data': 'exit', 'confidence': 1.0}
    >>> v2_run_keyword_evaluation("exi")  # doctest: +ELLIPSIS   
    {'type': 'keyword', 'data': 'exit', 'confidence': 0...}
    >>> v2_run_keyword_evaluation("eas")  # doctest: +ELLIPSIS
    {'type': 'keyword', 'data': 'easy', 'confidence': 0...}
    >>> v2_run_keyword_evaluation("hard")
    {'type': 'keyword', 'data': '', 'confidence': 0}
    >>> v2_run_keyword_evaluation("hardier")  # doctest: +ELLIPSIS
    {'type': 'keyword', 'data': 'harder', 'confidence': 0...}
    >>> v2_run_keyword_evaluation("I'm tired")  # doctest: +ELLIPSIS
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


def format_single_event_nlu_response(eval_type, result, confidence=1, intents=[]):
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


def build_evaluation_sequence_nlu_response_object(results):
    """ Builds a response that based on the outcome of all the evaluations 
    
    # TODO: Update test
    build_evaluation_sequence_nlu_response_object({'keyword': None, 'answer_extraction': 'Yes', 'numerical_extraction': None, 'intents': {'data': 'yes', 'confidence': 0.7285137685012592, 'intents': [{'type': 'intent', 'data': 'yes', 'confidence': 0.7285137685012592}, {'type': 'intent', 'data': 'next_lesson', 'confidence': 0.43764260237929115}, {'type': 'intent', 'data': 'spam', 'confidence': 0.39586822881508865}]}})
    {'type': 'answer_extraction', 'data': 'Yes', 'confidence': 0, 'intents': [{'type': 'intent', 'data': 'yes', 'confidence': 0.7285137685012592}, {'type': 'intent', 'data': 'next_lesson', 'confidence': 0.43764260237929115}, {'type': 'intent', 'data': 'spam', 'confidence': 0.39586822881508865}]}
    """
    print("results===============")
    print(results)
    print("==============")
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
    elif results.get('regex_number_extraction', ''):
        nlu_response['type'] = 'regex_number_extraction'
        nlu_response['data'] = results.get('regex_number_extraction', '')
    elif results.get('number_misspelling', ''):
        nlu_response['type'] = 'number_misspelling'
        nlu_response['data'] = results.get('number_misspelling', '')
    else:
        nlu_response['type'] = 'intent'
        try:
            nlu_response['data'] = results['intents']['intents'][0]['data']
            nlu_response['confidence'] = results['intents']['intents'][0]['confidence']
        except:
            nlu_response['data'] = 32202
            nlu_response['confidence'] = 0
    
    return nlu_response


async def v3_evaluate_message_with_nlu(message_text, expected_answer):
    """ Process a student's message using NLU functions and send the result

    # TODO: Update tests with new data structure and coroutine
    evaluate_message_with_nlu({"author_id": "57787919091", "author_type": "OWNER", "contact_uuid": "df78gsdf78df", "message_body": "8", "message_direction": "inbound", "message_id": "dfgha789789ag9ga", "message_inserted_at": "2023-01-10T02:37:28.487319Z", "message_updated_at": "2023-01-10T02:37:28.487319Z"})
    {'type': 'integer', 'data': 8, 'confidence': 0}

    evaluate_message_with_nlu({"author_id": "57787919091", "author_type": "OWNER", "contact_uuid": "df78gsdf78df", "message_body": "I am tired", "message_direction": "inbound", "message_id": "dfgha789789ag9ga", "message_inserted_at": "2023-01-10T02:37:28.487319Z", "message_updated_at": "2023-01-10T02:37:28.487319Z"})  # doctest: +ELLIPSIS
    {'type': 'intent', 'data': 'tired', 'confidence': 1.0}
    """
    with sentry_sdk.start_transaction(op="task", name="V3 NLU Evaluation"):
        # Call validate payload
        log.info(f'Starting evaluate message: {message_text}')

        result = ''
        normalized_student_message, normalized_expected_answer= normalize_message_and_answer(message_text, expected_answer)

        nlu_responses = {
            'text_extraction': None,
            'regex_answer_extraction': None,
            'regex_number_extraction': None,
            'number_misspelling': None,
            'intents': None
        }

        if len(message_text) < 50:
            # Check the student message for pre-defined keywords
            
            with sentry_sdk.start_span(description="V3 Comparison Evaluation"):
                if normalized_student_message.replace(' ', '') == normalized_expected_answer.replace(' ', ''):
                    return format_single_event_nlu_response(
                        'comparison',
                        expected_answer
                    )

            with sentry_sdk.start_span(description="V3 Text Evaluation"):
                tokenized_student_message = normalized_student_message.split()

                extracted_approved_response = extract_approved_response_from_phrase(
                    tokenized_student_message,
                    normalized_expected_answer,
                    expected_answer
                )
                if extracted_approved_response:
                    nlu_responses['text_extraction'] = extracted_approved_response

            with sentry_sdk.start_span(description="V3 Regex Answer Evaluation"):
                result = regex_evaluation(normalized_student_message)
                if result:
                    nlu_responses['regex_answer_extraction'] = result


            with sentry_sdk.start_span(description="V3 Regex Number Evaluation"):
                result = extract_numbers_with_regex(
                    normalized_student_message,
                    normalized_expected_answer,
                    expected_answer
                )
                if result:
                    nlu_responses['regex_number_extraction'] = result

            with sentry_sdk.start_span(description="V3 Number Misspelling Evaluation"):
                result = [NUMBER_MAP[token] for token in tokenized_student_message if token in NUMBER_MAP]
                if result:
                    if str(sum(result)) == normalized_expected_answer:
                        nlu_responses['number_misspelling'] = result

        with sentry_sdk.start_span(description="V3 Model Evaluation"):
            # Run intent classification with logistic regression model
            result = run_intent_evaluation(message_text)
            nlu_responses['intents'] = {
                'data': result['data'],
                'confidence': result['confidence'],
                'intents': result['intents']
            }

    nlu_response = build_evaluation_sequence_nlu_response_object(nlu_responses)

    return nlu_response
