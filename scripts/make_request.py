import json
import requests


def add_message_text_to_sample_object(message_text):
    """
    Builds a sample request object using an example of a student answer

    Input
    - message_text: str - an example of user input to test

    Example Input
    "test message"

    Output
    - b_string: json b-string - simulated Turn.io message data

    Example Output
    b'{"context": "hi", "message_data": {"author_id": "+57787919091", "author_type": "OWNER", "contact_uuid": "j43hk26-2hjl-43jk-hnk2-k4ljl46j0ds09", "message_body": "test message", "message_direction": "inbound", "message_id": "4kl209sd0-a7b8-2hj3-8563-3hu4a89b32", "message_inserted_at": "2023-01-10T02:37:28.477940Z", "message_updated_at": "2023-01-10T02:37:28.487319Z"}}'
    
    """
    message_data = '{' + f'"author_id": "+57787919091", "author_type": "OWNER", "contact_uuid": "j43hk26-2hjl-43jk-hnk2-k4ljl46j0ds09", "message_body": "{message_text}", "message_direction": "inbound", "message_id": "4kl209sd0-a7b8-2hj3-8563-3hu4a89b32", "message_inserted_at": "2023-01-10T02:37:28.477940Z", "message_updated_at": "2023-01-10T02:37:28.487319Z"' + '}'

    context_data = '{' + '"contact_uuid": "j43hk26-2hjl-43jk-hnk2-k4ljl46j0ds09", "current_state":"", "local_state": "", "user_message":""' + '}'

    json_string = '{' + f'"context_data": {context_data}, "message_data": {message_data}' + '}'
    b_string = json_string.encode("utf-8")

    return b_string


def run_simulated_request(endpoint, sample_payload, context=None):
    print(f"Case: {sample_payload}")
    # Used for testing full message object - deprecated April 7
    b_string = add_message_text_to_sample_object(sample_payload)

    if endpoint == 'intent-recognition' or \
        endpoint == 'keyword-detection' or \
        endpoint == 'text2int':
        request = requests.post(
            url=f'http://localhost:7860/{endpoint}',
            json={'content': sample_payload}
        ).json()
    else:
        request = requests.post(
            url=f'http://localhost:7860/{endpoint}',
            data=b_string
        ).json()

    print(request)


def run_full_nlu_endpoint_payload_test(sample_payload):
    request = requests.post(
        url=f'http://localhost:7860/nlu',
        data=sample_payload
    ).json()
    print(request)


nlu_test_cases = [
    # 'test message',
    # 'is it 8',
    # 'can I know how its 0.5',
    # 'eight, nine, ten',
    # '8, 9, 10',
    # '8',
    # "I don't know",
    # "I don't know eight",
    # "I don't 9",
    # '0.2',
    # 'I want you to tell me'
    # 'Today is a wonderful day',
    # 'IDK 5?',
    # 'hin',
    # 'exi',
    # 'easier',
    # 'stp',
    # '',
    '11:00 PM',
    '12:45',
    "10 : 25 AM",
    "0:30",
    "7:00",
    "23:45",
    '~T[11:30:00]'
]

keyword_test_cases = [
    'exit',
    "esier",
    'easier',
    'easy',
    'harder',
    'hard',
    'hint',
    'hin',
    'stop',
    'stp',
    'sop',
    'please stop',
    "I'm not sure about that",
    "What should I do?"
]

intent_test_cases = [
    'exit',
    "I'm not sure",
    'easier',
    'easy',
    'What is this',
    'I want to do some math',
    'This sucks',
    'fuck you',
    "I'm so tired",
    "Thanks, Rori.  I'm having fun",
    "Maybe it's 8",
    'please stop',
    "I'm not sure about that",
    "What should I do?"
]

wormhole_test_cases = [
    '',
    'add',
    'subtract'
]


def run_set_of_tests(endpoint):
    if endpoint == 'nlu':
        test_cases = nlu_test_cases
    elif endpoint == 'keyword-detection':
        test_cases = keyword_test_cases
    elif endpoint == 'intent-recognition':
        test_cases = intent_test_cases
    elif endpoint == 'wormhole':
        test_cases = wormhole_test_cases
    else:
        return False

    for case in test_cases:
        run_simulated_request(endpoint, case)



# Case: Wrong payload object
if __name__ == '__main__':
    # Case: Full event object (Incorrect format)
    # run_full_nlu_endpoint_payload_test(b'{"message_data": {"_vnd": {"v1": {"author": {"id": 54327547257, "name": "Jin", "type": "OWNER"}, "card_uuid": None, "chat": {"assigned_to": None, "contact_uuid": "f7889-f78dfgb798-f786ah89g7-f78f9a", "inserted_at": "2023-03-28T13:21:47.581221Z", "owner": "+43789789146", "permalink": "", "state": "OPEN", "state_reason": "Re-opened by inbound message.", "unread_count": 97, "updated_at": "2023-04-07T21:05:27.389948Z", "uuid": "dfg9a78-d76a786dghas-78d9fga789g-a78d69a9"}, "direction": "inbound", "faq_uuid": None, "in_reply_to": None, "inserted_at": "2023-04-07T21:05:27.368580Z", "labels": [], "last_status": None, "last_status_timestamp": None, "on_fallback_channel": False, "rendered_content": None, "uuid": "hf78s7s89b-789fb68d9fg-789fb789dfb-f79sfb789"}}, "from": 5475248689, "id": "SBDE4zgAAy7887sfdT35SHFS", "text": {"body": 1000}, "timestamp": 1680901527, "type": "text"}, "type": "message"}')

    # These tests for validation of the payload from Turn.io
    # Case: Wrong key
    run_full_nlu_endpoint_payload_test(b'{"message": {"author_id": "@event.message._vnd.v1.chat.owner", "author_type": "@event.message._vnd.v1.author.type", "contact_uuid": "@event.message._vnd.v1.chat.contact_uuid", "message_body": "@event.message.text.body", "message_direction": "@event.message._vnd.v1.direction", "message_id": "@event.message.id", "message_inserted_at": "@event.message._vnd.v1.chat.inserted_at", "message_updated_at": "@event.message._vnd.v1.chat.updated_at"}}')

    # Case: Correct payload
    run_full_nlu_endpoint_payload_test(b'{"message_data": {"author_id": "57787919091", "author_type": "OWNER", "contact_uuid": "df78gsdf78df", "message_body": "8", "message_direction": "inbound", "message_id": "dfgha789789ag9ga", "message_inserted_at": "2023-01-10T02:37:28.487319Z", "message_updated_at": "2023-01-10T02:37:28.487319Z"}}')

    # Case: Correct payload + extra fields
    run_full_nlu_endpoint_payload_test(b'{"message_data": {"author_id": "57787919091", "author_type": "OWNER", "contact_uuid": "df78gsdf78df", "message_body": "8", "message_direction": "inbound", "message_id": "dfgha789789ag9ga", "message_inserted_at": "2023-01-10T02:37:28.487319Z", "message_updated_at": "2023-01-10T02:37:28.487319Z", "question": "What is next - 2, 6, 8?", "expected_answer": 8}}')

    # Case: Incorrect payload values
    run_full_nlu_endpoint_payload_test(b'{"message_data": {"author_id": "@event.message._vnd.v1.chat.owner", "author_type": "@event.message._vnd.v1.author.type", "contact_uuid": "@event.message._vnd.v1.chat.contact_uuid", "message_body": "@event.message.text.body", "message_direction": "@event.message._vnd.v1.direction", "message_id": "@event.message.id", "message_inserted_at": "@event.message._vnd.v1.chat.inserted_at", "message_updated_at": "@event.message._vnd.v1.chat.updated_at"}}')

    # These tests run through the nlu endpoints
    run_set_of_tests('nlu')
    # run_set_of_tests('intent-recognition')
    # run_set_of_tests('keyword-detection')

    # This test runs through wormhole conversation management functions
    # run_set_of_tests('manager')

    # These tests run on the data-drive-quiz
    # run_simulated_request("start", {
    #     'difficulty': 0.04,
    #     'do_increase': True
    # })
    # run_simulated_request("hint", {
    #     'start': 5,
    #     'step': 1,
    #     'difficulty': 0.56  # optional
    # })
    # run_simulated_request("question", {
    #     'start': 2,
    #     'step': 1,
    #     'question_num': 2  # optional
    # })
    # run_simulated_request("difficulty", {
    #     'difficulty': 0.01,
    #     'do_increase': False  # True | False
    # })
    # Need to start with this command to populate users.json
    # If users.json is not already made
    # run_simulated_request("num_one", {
    #     "user_id": "1",
    #     "message_text": "",
    # })
    # run_simulated_request("num_one", {
    #     "user_id": "1",
    #     "message_text": "61",
    # })
    # run_simulated_request("sequence", {
    #     'start': 2,
    #     'step': 1,
    #     'sep': '... '
    # })

    # run_simulated_request('manager', 'exit')





# Example of simplified object received from Turn.io stacks
# This is a contrived example to show the structure, not an actual state
# NOTE: This is actually a bstring, not a dict
# simplified_json = {
#     "context": {
#         "user": "+57787919091",
#         "state": "answer-addition-problem",
#         "bot_message": "What is 2+2?",
#         "user_message": "eight",
#         "type": "ask"
#     },
#     "message_data": {
#         "author_id": "+57787919091",
#         "author_type": "OWNER",
#         "contact_uuid": "j43hk26-2hjl-43jk-hnk2-k4ljl46j0ds09",
#         "message_body": "eight",
#         "message_direction": "inbound",
#         "message_id": "4kl209sd0-a7b8-2hj3-8563-3hu4a89b32",
#         "message_inserted_at": "2023-01-10T02:37:28.477940Z",
#         "message_updated_at": "2023-01-10T02:37:28.487319Z"
#     }
# }


# Full example of event data from Turn.io
# simplified_json is built from this in Turn.io
# full_json = {
#     'message': {
#         '_vnd': {
#             'v1': {
#                 'author': {
#                     'id': 57787919091,
#                     'name': 'GT',
#                     'type': 'OWNER'
#                 },
#                 'card_uuid': None,
#                 'chat': {
#                     'assigned_to': {
#                         'id': 'jhk151kl-hj42-3752-3hjk-h4jk6hjkk2',
#                         'name': 'Greg Thompson',
#                         'type': 'OPERATOR'
#                     },
#                     'contact_uuid': 'j43hk26-2hjl-43jk-hnk2-k4ljl46j0ds09',
#                     'inserted_at': '2022-07-05T04:00:34.033522Z',
#                     'owner': '+57787919091',
#                     'permalink': 'https://app.turn.io/c/4kl209sd0-a7b8-2hj3-8563-3hu4a89b32',
#                     'state': 'OPEN',
#                     'state_reason': 'Re-opened by inbound message.',
#                     'unread_count': 19,
#                     'updated_at': '2023-01-10T02:37:28.487319Z',
#                     'uuid': '4kl209sd0-a7b8-2hj3-8563-3hu4a89b32'
#                 },
#                 'direction': 'inbound',
#                 'faq_uuid': None,
#                 'in_reply_to': None,
#                 'inserted_at': '2023-01-10T02:37:28.477940Z',
#                 'labels': [{
#                     'confidence': 0.506479332,
#                     'metadata': {
#                         'nlu': {
#                             'confidence': 0.506479332,
#                             'intent': 'question',
#                             'model_name': 'nlu-general-spacy-ngrams-20191014'
#                         }
#                     },
#                     'uuid': 'ha7890s2k-hjk2-2476-s8d9-fh9779a8a9ds',
#                     'value': 'Unclassified'
#                 }],
#                 'last_status': None,
#                 'last_status_timestamp': None,
#                 'on_fallback_channel': False,
#                 'rendered_content': None,
#                 'uuid': 's8df79zhws-h89s-hj23-7s8d-thb248d9bh2qn'
#             }
#         },
#         'from': 57787919091,
#         'id': 'hsjkthzZGehkzs09sijWA3',
#         'text': {'body': 'eight'},
#         'timestamp': 1673318248,
#         'type': 'text'
#     },
#     'type': 'message'
# }
