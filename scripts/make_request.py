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
    context_data = '{' + '"user":"", "state":"start-conversation", "bot_message":"", "user_message":"{message_text}"' + '}'

    json_string = '{' + f'"context_data": {context_data}, "message_data": {message_data}' + '}'
    b_string = json_string.encode("utf-8")

    return b_string


def run_simulated_request(endpoint, sample_answer, context=None):
    print(f"Case: {sample_answer}")
    b_string = add_message_text_to_sample_object(sample_answer)

    if endpoint == 'sentiment-analysis' or endpoint == 'text2int':
        request = requests.post(
            url=f'http://localhost:7860/{endpoint}',
            json={'content': sample_answer}
        ).json()
    else:
        request = requests.post(
            url=f'http://localhost:7860/{endpoint}',
            data=b_string
        ).json()

    print(request)


# run_simulated_request('sentiment-analysis', 'I reject it')
# run_simulated_request('text2int', 'seven thousand nine hundred fifty seven')
# run_simulated_request('nlu', 'test message')
# run_simulated_request('nlu', 'eight')
# run_simulated_request('nlu', 'eight, nine, ten')
# run_simulated_request('nlu', '8, 9, 10')
# run_simulated_request('nlu', '8')
# run_simulated_request('nlu', "I don't know")
# run_simulated_request('nlu', 'Today is a wonderful day')
# run_simulated_request('nlu', 'IDK 5?')
# run_simulated_request('manager', '')
run_simulated_request('manager', 'add')
# run_simulated_request('manager', 'subtract')
# run_simulated_request('manager', 'exit')


# Example of simplified object received from Turn.io stacks
# This is a contrived example to show the structure, not an actual state
# NOTE: This is actually a bstring, not a dict
simplified_json = {
    "context": {
        "user": "+57787919091", 
        "state": "answer-addition-problem", 
        "bot_message": "What is 2+2?", 
        "user_message": "eight",
        "type": "ask"
    },
    "message_data": {
        "author_id": "+57787919091", 
        "author_type": "OWNER", 
        "contact_uuid": "j43hk26-2hjl-43jk-hnk2-k4ljl46j0ds09", 
        "message_body": "eight", 
        "message_direction": "inbound", 
        "message_id": "4kl209sd0-a7b8-2hj3-8563-3hu4a89b32", 
        "message_inserted_at": "2023-01-10T02:37:28.477940Z", 
        "message_updated_at": "2023-01-10T02:37:28.487319Z"
    }
}


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
