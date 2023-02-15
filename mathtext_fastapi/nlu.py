from mathtext_fastapi.logging import prepare_message_data_for_logging
from mathtext.sentiment import sentiment
from mathtext.text2int import text2int
import re


def build_nlu_response_object(type, data, confidence):
    """ Builds a json object from the result of nlu functions to send back to Turn.io
    Inputs
    - type: str - the type of nlu run (integer or sentiment-analysis)
    - data: str - the student message
    - confidence: - the nlu confidence score.  Integer is ''.  Sentiment analysis is a float
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
        nlu_response = build_nlu_response_object('integer', ','.join(message_text_arr), '')
        prepare_message_data_for_logging(message_data, nlu_response)
    return nlu_response


def run_text2int_on_each_list_item(message_text_arr):
    """ Checks each item in an array to see if it can be converted to an integer

    Input
    - message_text_arr: list - a set of text extracted from the student message

    Output
    - student_response_arr: list - a set of integers derived from the nlu function
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
    message_text = message_data['message_body']
    message_text_arr = re.split(", |,| ", message_text.strip())

    # TODO: Replace this with appropriate utility function (is_int, is_float, render_int_or_float)
    nlu_response = test_for_float_or_int(message_data, message_text)
    if len(nlu_response) > 0:
        return nlu_response

    # TODO: Replace this with appropriate utility function
    nlu_response = test_for_number_sequence(message_text_arr, message_data, message_text)
    if len(nlu_response) > 0:
        return nlu_response

    student_response_arr = run_text2int_on_each_list_item(message_text_arr)

    # '32202' is text2int's error code for non-integer student answers (ie., "I don't know")
    # If any part of the list is 32202, sentiment analysis will run
    # TODO: Need to replace this with logic that recognizes multiple intents (Maybe 36 = "sentiment analysis" & "integer")
    student_response_arr = run_text2int_on_each_list_item(message_text_arr)
    if 32202 in student_response_arr:
        sentiment_api_resp = sentiment(message_text)
        nlu_response = build_nlu_response_object('sentiment', sentiment_api_resp[0]['label'], sentiment_api_resp[0]['score'])
    else:
        if len(student_response_arr) > 1:
            nlu_response = build_nlu_response_object('integer', ','.join(str(num) for num in student_response_arr), '' )
        else:
            nlu_response = build_nlu_response_object('integer', student_response_arr[0], '')

    prepare_message_data_for_logging(message_data, nlu_response)
    return nlu_response


