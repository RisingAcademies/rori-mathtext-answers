from mathtext_fastapi.logging import prepare_message_data_for_logging
from mathtext.sentiment import sentiment
from mathtext.text2int import text2int
import re


def build_nlu_response_object(type, data, confidence):
    """ Turns nlu results into an object to send back to Turn.io
    Inputs
    - type: str - the type of nlu run (integer or sentiment-analysis)
    - data: str - the student message
    - confidence: - the nlu confidence score (sentiment) or '' (integer)
    """
    return {'type': type, 'data': data, 'confidence': confidence}


def test_for_float_or_int(message_data, message_text):
    nlu_response = {}
    if type(message_text) == int or type(message_text) == float:
        nlu_response = build_nlu_response_object('integer', message_text, '')
        prepare_message_data_for_logging(message_data, nlu_response)
    return nlu_response


def test_for_number_sequence(message_text_arr, message_data, message_text):
    nlu_response = {}
    if all(ele.isdigit() for ele in message_text_arr):
        nlu_response = build_nlu_response_object(
            'integer',
            ','.join(message_text_arr),
            ''
        )
        prepare_message_data_for_logging(message_data, nlu_response)
    return nlu_response


def run_text2int_on_each_list_item(message_text_arr):
    """ Attempts to convert each list item to an integer

    Input
    - message_text_arr: list - a set of text extracted from the student message

    Output
    - student_response_arr: list - a set of integers (32202 for error code)
    """
    student_response_arr = []
    for student_response in message_text_arr:
        int_api_resp = text2int(student_response.lower())
        student_response_arr.append(int_api_resp)
    return student_response_arr


def run_sentiment_analysis(message_text):
    # TODO: Add intent labelling here
    # TODO: Add logic to determine whether intent labeling or sentiment analysis is more appropriate (probably default to intent labeling)
    return sentiment(message_text)


def evaluate_message_with_nlu(message_data):
    # Keeps system working with two different inputs - full and filtered @event object
    try:
        message_text = message_data['message_body']
    except KeyError:
        message_data = {
            'author_id': message_data['message']['_vnd']['v1']['chat']['owner'],
            'author_type': message_data['message']['_vnd']['v1']['author']['type'],
            'contact_uuid': message_data['message']['_vnd']['v1']['chat']['contact_uuid'],
            'message_body': message_data['message']['text']['body'],
            'message_direction': message_data['message']['_vnd']['v1']['direction'],
            'message_id': message_data['message']['id'],
            'message_inserted_at': message_data['message']['_vnd']['v1']['chat']['inserted_at'],
            'message_updated_at': message_data['message']['_vnd']['v1']['chat']['updated_at'],
        }
        message_text = message_data['message_body']

    number_api_resp = text2int(message_text.lower())

    if number_api_resp == 32202:
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
            ''
        )

    prepare_message_data_for_logging(message_data, nlu_response)
    return nlu_response
