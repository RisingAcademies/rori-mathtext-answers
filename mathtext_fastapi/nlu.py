from logging import getLogger
import re

from fuzzywuzzy import fuzz
from mathtext_fastapi.logging import prepare_message_data_for_logging
from mathtext.sentiment import sentiment
from mathtext.text2int import text2int
from mathtext_fastapi.intent_classification import create_intent_classification_model, retrieve_intent_classification_model, predict_message_intent

log = getLogger(__name__)

ERROR_CODE = 32202

def build_nlu_response_object(type, data, confidence):
    """ Turns nlu results into an object to send back to Turn.io
    Inputs
    - type: str - the type of nlu run (integer or sentiment-analysis)
    - data: str/int - the student message
    - confidence: - the nlu confidence score (sentiment) or '' (integer)

    >>> build_nlu_response_object('integer', 8, 0)
    {'type': 'integer', 'data': 8, 'confidence': 0}

    >>> build_nlu_response_object('sentiment', 'POSITIVE', 0.99)
    {'type': 'sentiment', 'data': 'POSITIVE', 'confidence': 0.99}
    """
    return {'type': type, 'data': data, 'confidence': confidence}


# def test_for_float_or_int(message_data, message_text):
#     nlu_response = {}
#     if type(message_text) == int or type(message_text) == float:
#         nlu_response = build_nlu_response_object('integer', message_text, '')
#         prepare_message_data_for_logging(message_data, nlu_response)
#     return nlu_response


def test_for_number_sequence(message_text_arr, message_data, message_text):
    """ Determines if the student's message is a sequence of numbers

    >>> test_for_number_sequence(['1','2','3'], {"author_id": "57787919091", "author_type": "OWNER", "contact_uuid": "df78gsdf78df", "message_body": "I am tired", "message_direction": "inbound", "message_id": "dfgha789789ag9ga", "message_inserted_at": "2023-01-10T02:37:28.487319Z", "message_updated_at": "2023-01-10T02:37:28.487319Z"}, '1, 2, 3')
    {'type': 'integer', 'data': '1,2,3', 'confidence': 0}

    >>> test_for_number_sequence(['a','b','c'], {"author_id": "57787919091", "author_type": "OWNER", "contact_uuid": "df78gsdf78df", "message_body": "I am tired", "message_direction": "inbound", "message_id": "dfgha789789ag9ga", "message_inserted_at": "2023-01-10T02:37:28.487319Z", "message_updated_at": "2023-01-10T02:37:28.487319Z"}, 'a, b, c')
    {}
    """
    nlu_response = {}
    if all(ele.isdigit() for ele in message_text_arr):
        nlu_response = build_nlu_response_object(
            'integer',
            ','.join(message_text_arr),
            0
        )
        prepare_message_data_for_logging(message_data, nlu_response)
    return nlu_response


def run_text2int_on_each_list_item(message_text_arr):
    """ Attempts to convert each list item to an integer

    Input
    - message_text_arr: list - a set of text extracted from the student message

    Output
    - student_response_arr: list - a set of integers (32202 for error code)

    >>> run_text2int_on_each_list_item(['1','2','3'])
    [1, 2, 3]
    """
    student_response_arr = []
    for student_response in message_text_arr:
        int_api_resp = text2int(student_response.lower())
        student_response_arr.append(int_api_resp)
    return student_response_arr


def run_sentiment_analysis(message_text):
    """ Evaluates the sentiment of a student message

    >>> run_sentiment_analysis("I am tired")
    [{'label': 'NEGATIVE', 'score': 0.9997807145118713}]

    >>> run_sentiment_analysis("I am full of joy")
    [{'label': 'POSITIVE', 'score': 0.999882698059082}]
    """
    # TODO: Add intent labelling here
    # TODO: Add logic to determine whether intent labeling or sentiment analysis is more appropriate (probably default to intent labeling)
    return sentiment(message_text)


def run_intent_classification(message_text):
    """ Process a student's message using basic fuzzy text comparison

    >>> run_intent_classification("exit")
    {'type': 'intent', 'data': 'exit', 'confidence': 1.0}
    >>> run_intent_classification("exi")     
    {'type': 'intent', 'data': 'exit', 'confidence': 0.86}
    >>> run_intent_classification("eas")
    {'type': 'intent', 'data': '', 'confidence': 0}
    >>> run_intent_classification("hard")
    {'type': 'intent', 'data': '', 'confidence': 0}
    >>> run_intent_classification("hardier") 
    {'type': 'intent', 'data': 'harder', 'confidence': 0.92}
    """
    label = ''
    ratio = 0
    nlu_response = {'type': 'intent', 'data': label, 'confidence': ratio}
    commands = [
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
        'please',
        'understand',
        'question',
        'easier',
        'easy',
        'support'
    ]
    
    for command in commands:
        try:
            ratio = fuzz.ratio(command, message_text.lower())
        except:
            ratio = 0
        if ratio > 80:
            nlu_response['data'] = command
            nlu_response['confidence'] = ratio / 100
    
    return nlu_response


def evaluate_message_with_nlu(message_data):
    """ Process a student's message using NLU functions and send the result
    
    >>> evaluate_message_with_nlu({"author_id": "57787919091", "author_type": "OWNER", "contact_uuid": "df78gsdf78df", "message_body": "8", "message_direction": "inbound", "message_id": "dfgha789789ag9ga", "message_inserted_at": "2023-01-10T02:37:28.487319Z", "message_updated_at": "2023-01-10T02:37:28.487319Z"})
    {'type': 'integer', 'data': 8, 'confidence': 0}

    >>> evaluate_message_with_nlu({"author_id": "57787919091", "author_type": "OWNER", "contact_uuid": "df78gsdf78df", "message_body": "I am tired", "message_direction": "inbound", "message_id": "dfgha789789ag9ga", "message_inserted_at": "2023-01-10T02:37:28.487319Z", "message_updated_at": "2023-01-10T02:37:28.487319Z"})
    {'type': 'sentiment', 'data': 'NEGATIVE', 'confidence': 0.9997807145118713}
    """
    # Keeps system working with two different inputs - full and filtered @event object
    log.info(f'Starting evaluate message: {message_data}')
    try:
        message_text = str(message_data.get('message_body', ''))
    except:
        log.error(f'Invalid request payload: {message_data}')
        # use python logging system to do this//
        return {'type': 'error', 'data': ERROR_CODE, 'confidence': 0}

    # Run intent classification only for keywords
    intent_api_response = run_intent_classification(message_text)
    if intent_api_response['data']:
        prepare_message_data_for_logging(message_data, intent_api_response)
        return intent_api_response

    number_api_resp = text2int(message_text.lower())

    if number_api_resp == ERROR_CODE:
        # Run intent classification with logistic regression model
        predicted_label = predict_message_intent(message_text)
        if predicted_label['confidence'] > 0.01:
            nlu_response = predicted_label
        else:
            # Run sentiment analysis
            sentiment_api_resp = sentiment(message_text)
            nlu_response = build_nlu_response_object(
                'sentiment',
                sentiment_api_resp[0]['label'],
                sentiment_api_resp[0]['score']
            )
    else:
        nlu_response = build_nlu_response_object(
            'integer',
            number_api_resp,
            0
        )

    prepare_message_data_for_logging(message_data, nlu_response)
    return nlu_response
