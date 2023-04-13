import base64
import dill
import os
import json
import jsonpickle
import pickle
import random
import requests

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
        # FIXME: Better to use "message_type" (but be careful with refactor)
        "type": "text",
        "text": {
            "body": message_text
        }
    }
    return message_data


def create_button_objects(button_options):
    """ Creates a list of button objects using the input values
    Input
    - button_options: list - a list of text to be displayed in buttons

    Output
    - button_arr: list - preformatted button objects filled with the inputs

    NOTE: Not fully implemented and tested
    """
    button_arr = []
    for option in button_options:
        button_choice = {
            "type": "reply",
            "reply": {
                "id": "inquiry-yes",
                "title": option['text']
            }
        }
        button_arr.append(button_choice)
    return button_arr


def create_interactive_message(message_text, button_options, whatsapp_id):
    """ Fills a template to create a button message for Whatsapp

    * NOTE: Not fully implemented and tested
    * NOTE/TODO: It is possible to create other kinds of messages
                 with the 'interactive message' template
    * Documentation:
      https://whatsapp.turn.io/docs/api/messages#interactive-messages

    Inputs
    - message_text: str - the content that the message should display
    - button_options: list - what each button option should display
    - whatsapp_id: str - the message recipient's phone number
    """
    button_arr = create_button_objects(button_options)

    data = {
        "to": whatsapp_id,
        "type": "interactive",
        "interactive": {
            "type": "button",
            # "header": { },
            "body": {
                "text": message_text
            },
            # "footer": { },
            "action": {
                "buttons": button_arr
            }
        }
    }
    return data


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


    # Make a completely new entry
    if fsm_check.data == []:
        # FIXME: Try not to use the Python reserved keyword `type` as a variable name
        #        It's better to use `kind` or `convo_type` or `convo_name`
        #        And the variable `type` is not defined here so I don't understand how this is working at all.
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


def use_quiz_module_approach(user_message, context_data):
    print("USER MESSAGE")
    print(user_message)
    print("=======================")
    if user_message == 'add':
        context_result = start_interactive_math()
        message_package = {
            'messages': [
                "Great, let's do some addition",
                "First, we'll start with single digits.",
                "Type your response as a number.  For example, for '1 + 1', you'd write 2."
            ],
            'input_prompt': context_result['text'],
            'state': "addition-question-sequence"
        }

    elif user_message == context_data.get('right_answer'):
        context_result = start_interactive_math(
            context_data['number_correct'],
            context_data['number_incorrect'],
            context_data['level']
        )
        message_package = {
            'messages': [
                "That's right, great!",
            ],
            'input_prompt': context_result['text'],
            'state': "addition-question-sequence"
        }
    else:
        context_result = generate_hint(
            context_data['question_numbers'],
            context_data['right_answer'],
            context_data['number_correct'],
            context_data['number_incorrect'],
            context_data['level'],
            context_data['hints_used']
        )
        message_package = {
            'messages': [
                context_result['text'],
            ],
            'input_prompt': context_data['text'],
            'state': "addition-question-sequence"
        }
    return message_package, context_result


def return_next_conversational_state(context_data, user_message, contact_uuid):
    """ Evaluates the conversation's current state to determine the next state

    Input
    - context_data: dict - data about the conversation's current state
    - user_message: str - the message the user sent in response to the state

    Output
    - message_package: dict - a series of messages and prompt to send
    """
    if context_data['user_message'] == '' and \
       context_data['state'] == 'start-conversation':
        message_package = {
            'messages': [],
            'input_prompt': "Welcome to our math practice.  What would you like to try?  Type add or subtract.",
            'state': "welcome-sequence"
        }
    elif context_data['state'] == 'addition-question-sequence' or \
        user_message == 'add':

        # Used in FSM
        # messages = manage_math_quiz_fsm(user_message, contact_uuid)

        # message_package, context_result = use_quiz_module_approach(user_message, context_data)
        messages = manage_math_quiz_fsm(user_message, contact_uuid, 'addition')

        if user_message == 'exit':
            state_label = 'exit'
        else:
            state_label = 'addition-question-sequence'
        # Used in FSM
        input_prompt = messages.pop()
        message_package = {
            'messages': messages,
            'input_prompt': input_prompt,
            'state': state_label
        }

        # Used in quiz w/ hints
        # context_data = context_result
        # message_package['state'] = state_label

    elif context_data['state'] == 'subtraction-question-sequence' or \
        user_message == 'subtract':
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

        # message_package = {
        #     'messages': [
        #         "Time for some subtraction!",
        #         "Type your response as a number.  For example, for '1 - 1', you'd write 0."
        #     ],
        #     'input_prompt': "Here's the first one... What's 3-1?",
        #     'state': "subtract-question-sequence"
        # }
    elif context_data['state'] == 'exit' or user_message == 'exit':
        message_package = {
            'messages': [
                "Great, thanks for practicing math today.  Come back any time."
            ],
            'input_prompt': "",
            'state': "exit"
        }
    else:
        message_package = {
            'messages': [
                "Hmmm...sorry friend.  I'm not really sure what to do."
            ],
            'input_prompt': "Please type add or subtract to start a math activity.",
            'state': "reprompt-menu-options"
        }
    # Used in FSM
    return message_package

    # Used in quiz folder approach
    # return context_result, message_package


def manage_conversation_response(data_json):
    """ Calls functions necessary to determine message and context data to send

    Input
    - data_json: dict - message data from Turn.io/Whatsapp

    Output
    - context: dict - a record of the state at a given point a conversation

    TODOs
    - implement logging of message
    - test interactive messages
    - review context object and re-work to use a standardized format
    - review ways for more robust error handling
    - need to make util functions that apply to both /nlu and /conversation_manager
    """
    message_data = data_json.get('message_data', '')
    context_data = data_json.get('context_data', '')

    whatsapp_id = message_data['author_id']
    user_message = message_data['message_body']
    contact_uuid = message_data['contact_uuid']

    # TODO: Need to incorporate nlu_response into wormhole by checking answers against database (spreadsheet?)
    nlu_response = evaluate_message_with_nlu(message_data)

    if context_data['state'] == 'addition':
        context_result, message_package = return_next_conversational_state(
            context_data,
            user_message,
            contact_uuid
        )
    else:
        message_package = return_next_conversational_state(
            context_data,
            user_message,
            contact_uuid
        )

    headers = {
        'Authorization': f"Bearer {os.environ.get('TURN_AUTHENTICATION_TOKEN')}",
        'Content-Type': 'application/json'
    }

    # Send all messages for the current state before a user input prompt (text/button input request)
    for message in message_package['messages']:
        data = create_text_message(message, whatsapp_id)

        print("data")
        print(data)

        r = requests.post(
            f'https://whatsapp.turn.io/v1/messages',
            data=json.dumps(data),
            headers=headers
        )

    # Update the context object with the new state of the conversation
    if context_data['state'] == 'addition':
        context = {
            "context": {
                "user": whatsapp_id,
                "state": message_package['state'],
                "bot_message": message_package['input_prompt'],
                "user_message": user_message,
                "type": 'ask',
                # Necessary for quiz folder approach
                "text": context_result.get('text'),
                "question_numbers": context_result.get('question_numbers'),
                "right_answer": context_result.get('right_answer'),
                "number_correct": context_result.get('number_correct'),
                "hints_used": context_result.get('hints_used'),
            }
        }
    else:
        context = {
            "context": {
                "user": whatsapp_id,
                "state": message_package['state'],
                "bot_message": message_package['input_prompt'],
                "user_message": user_message,
                "type": 'ask',
            }
        }

    return context

    # data = {
    #     "to": whatsapp_id,
    #     "type": "interactive",
    #     "interactive": {
    #         "type": "button",
    #         # "header": { },
    #         "body": {
    #             "text": "Did I answer your question?"
    #         },
    #         # "footer": { },
    #         "action": {
    #             "buttons": [
    #                 {
    #                     "type": "reply",
    #                     "reply": {
    #                         "id": "inquiry-yes",
    #                         "title": "Yes"
    #                     }
    #                 },
    #                 {
    #                     "type": "reply",
    #                     "reply": {
    #                         "id": "inquiry-no",
    #                         "title": "No"
    #                     }
    #                 }
    #             ]
    #         }
    #     }
    # }
