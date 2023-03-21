import base64
import copy
import dill
import os
import json
import jsonpickle
import pickle
import random
import requests
import mathtext_fastapi.global_state_manager as gsm

from dotenv import load_dotenv
from mathtext_fastapi.nlu import evaluate_message_with_nlu
from mathtext_fastapi.math_quiz_fsm import MathQuizFSM
from mathtext_fastapi.math_subtraction_fsm import MathSubtractionFSM
from supabase import create_client
from transitions import Machine

from mathactive.generators import start_interactive_math
from mathactive.hints import generate_hint

load_dotenv()

SUPA = create_client(
    os.environ.get('SUPABASE_URL'),
    os.environ.get('SUPABASE_KEY')
)


def pickle_and_encode_state_machine(state_machine):
    dump = pickle.dumps(state_machine)
    dump_encoded = base64.b64encode(dump).decode('utf-8')
    return dump_encoded


def manage_math_quiz_fsm(user_message, contact_uuid, type):
    fsm_check = SUPA.table('state_machines').select("*").eq(
        "contact_uuid",
        contact_uuid
    ).execute()

    # This doesn't allow for when one FSM is present and the other is empty
    """
    1
    data=[] count=None
    
    2
    data=[{'id': 29, 'contact_uuid': 'j43hk26-2hjl-43jk-hnk2-k4ljl46j0ds09', 'addition3': None, 'subtraction': None, 'addition': 

    - but problem is there is no subtraction , but it's assuming there's a subtration

    Cases
    - make a completely new record
    - update an existing record with an existing FSM
    - update an existing record without an existing FSM
    """
    print("MATH QUIZ FSM ACTIVITY")
    print("user_message")
    print(user_message)
    # Make a completely new entry
    if fsm_check.data == []:
        if type == 'addition':
            math_quiz_state_machine = MathQuizFSM()
        else:
            math_quiz_state_machine = MathSubtractionFSM()
        messages = [math_quiz_state_machine.response_text]
        dump_encoded = pickle_and_encode_state_machine(math_quiz_state_machine)

        SUPA.table('state_machines').insert({
            'contact_uuid': contact_uuid,
            f'{type}': dump_encoded
        }).execute()
    # Update an existing record with a new state machine
    elif not fsm_check.data[0][type]:
        if type == 'addition':
            math_quiz_state_machine = MathQuizFSM()
        else:
            math_quiz_state_machine = MathSubtractionFSM()
        messages = [math_quiz_state_machine.response_text]
        dump_encoded = pickle_and_encode_state_machine(math_quiz_state_machine)

        SUPA.table('state_machines').update({
            f'{type}': dump_encoded
        }).eq(
            "contact_uuid", contact_uuid
        ).execute()      
    # Update an existing record with an existing state machine
    elif fsm_check.data[0][type]:
        undump_encoded = base64.b64decode(
            fsm_check.data[0][type].encode('utf-8')
        )
        math_quiz_state_machine = pickle.loads(undump_encoded)

        math_quiz_state_machine.student_answer = user_message
        math_quiz_state_machine.correct_answer = str(math_quiz_state_machine.correct_answer)
        messages = math_quiz_state_machine.validate_answer()
        dump_encoded = pickle_and_encode_state_machine(math_quiz_state_machine)          
        SUPA.table('state_machines').update({
            f'{type}': dump_encoded
        }).eq(
            "contact_uuid", contact_uuid
        ).execute()
    return messages


def retrieve_microlesson_content(context_data, user_message, microlesson, contact_uuid):
    if context_data['local_state'] == 'addition-question-sequence' or \
        user_message == 'add' or \
        microlesson == 'addition':
        messages = manage_math_quiz_fsm(user_message, contact_uuid, 'addition')

        if user_message == 'exit':
            state_label = 'exit'
        else:
            state_label = 'addition-question-sequence'

        input_prompt = messages.pop()
        message_package = {
            'messages': messages,
            'input_prompt': input_prompt,
            'state': state_label
        }
    elif microlesson == 'addition2':
        pass
        # message_package = mathactive.process_user_message(user_id, message_text, state)
    elif context_data['local_state'] == 'subtraction-question-sequence' or \
        user_message == 'subtract' or \
        microlesson == 'subtraction':
        messages = manage_math_quiz_fsm(user_message, contact_uuid, 'subtraction')

        if user_message == 'exit':
            state_label = 'exit'
        else:
            state_label = 'subtraction-question-sequence'

        input_prompt = messages.pop()

        message_package = {
            'messages': messages,
            'input_prompt': input_prompt,
            'state': state_label
        }
    print("MICROLESSON CONTENT RESPONSE")
    print(message_package)
    return message_package


curriculum_lookup_table = {
    'N1.1.1_G1': 'addition',
    'N1.1.1_G2': 'addition2',
    'N1.1.2_G1': 'subtraction'
}


def lookup_local_state(next_state):
    microlesson = curriculum_lookup_table[next_state]
    return microlesson


def create_text_message(message_text, whatsapp_id):
    """ Fills a template with input values to send a text message to Whatsapp

    Inputs
    - message_text: str - the content that the message should display
    - whatsapp_id: str - the message recipient's phone number

    Outputs
    - message_data: dict - a preformatted template filled with inputs
    """
    message_data = {
        "preview_url": False,
        "recipient_type": "individual",
        "to": whatsapp_id,
        "type": "text",
        "text": {
            "body": message_text
        }
    }
    return message_data


def manage_conversation_response(data_json):
    """ Calls functions necessary to determine message and context data """
    print("V2 ENDPOINT")

    user_message = ''
    # whatsapp_id = data_json['author_id']
    message_data = data_json['message_data']
    context_data = data_json['context_data']
    whatsapp_id = message_data['author_id']
    print("MESSAGE DATA")
    print(message_data)
    print("CONTEXT DATA")
    print(context_data)
    print("=================")

    # nlu_response = evaluate_message_with_nlu(message_data)

    # context_data = {
    #     'contact_uuid': 'abcdefg',
    #     'current_state': 'N1.1.1_G2',
    #     'user_message': '1',
    #     'local_state': ''
    # }
    print("STEP 1")
    print(data_json)
    if not context_data['current_state']:
        context_data['current_state'] = 'N1.1.1_G1'

    curriculum_copy = copy.deepcopy(gsm.curriculum)

    print("STEP 2")
    if context_data['user_message'] == 'easier':
        curriculum_copy.left()
        next_state = curriculum_copy.state
    elif context_data['user_message'] == 'harder':
        curriculum_copy.right()
        next_state = curriculum_copy.state
    else:
        next_state = context_data['current_state']

    print("STEP 3")
    microlesson = lookup_local_state(next_state)

    print("microlesson")
    print(microlesson)

    microlesson_content = retrieve_microlesson_content(context_data, context_data['user_message'], microlesson, context_data['contact_uuid'])

    headers = {
        'Authorization': f"Bearer {os.environ.get('TURN_AUTHENTICATION_TOKEN')}",
        'Content-Type': 'application/json'
    }

    # Send all messages for the current state before a user input prompt (text/button input request)
    for message in microlesson_content['messages']:
        data = create_text_message(message, whatsapp_id)

        print("data")
        print(data)

        r = requests.post(
            f'https://whatsapp.turn.io/v1/messages',
            data=json.dumps(data),
            headers=headers
        )

    print("STEP 4")
    # combine microlesson content and context_data object

    updated_context = {
        "context": {
            "contact_id": whatsapp_id,
            "contact_uuid": context_data['contact_uuid'],
            "state": microlesson_content['state'],
            "bot_message": microlesson_content['input_prompt'],
            "user_message": user_message,
            "type": 'ask'
        }
    }
    return updated_context
