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

from scripts.quiz.generators import start_interactive_math
from scripts.quiz.hints import generate_hint

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
    'N1.1.1_G2': 'subtraction'
}


def lookup_local_state(next_state):
    microlesson = curriculum_lookup_table[next_state]
    return microlesson


def manage_conversation_response(data_json):
    """ Calls functions necessary to determine message and context data """
    print("V2 ENDPOINT")

    user_message = ''

    # nlu_response = evaluate_message_with_nlu(message_data)

    context_data = {
        'contact_uuid': 'abcdefg',
        'current_state': 'N1.1.1_G2',
        'user_message': '1',
        'local_state': ''
    }
    print("STEP 1")
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

    print("STEP 4")
    # combine microlesson content and context_data object
    return context_data
