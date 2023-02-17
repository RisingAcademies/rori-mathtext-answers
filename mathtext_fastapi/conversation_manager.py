import dill as pickle
import os
import json
import random
import requests

from dotenv import load_dotenv
from mathtext_fastapi.nlu import evaluate_message_with_nlu
from math_quiz_fsm import MathQuizFSM

from transitions import Machine

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
    elif user_message == 'add':

        fsm_check = SUPA.table('state_machines').select("*").eq(
            "uuid",
            contact_uuid
        ).execute()

        if fsm_check.data == []:
            math_quiz_state_machine = MathQuizFSM()
            messages = [math_quiz_state_machine.response_text]
            dump = pickle.dumps(math_quiz_state_machine)

            # TODO: Check how to save - JSONB?
            SUPA.table('state_machines').insert(dump).execute()
        else:
            math_quiz_state_machine = pickle.loads(fsm_check.data['add'])
            math_quiz_state_machine.student_answer
            messages = math_quiz_state_machine.validate()
            dump = pickle.dumps(math_quiz_state_machine)            
            SUPA.table('state_machines').update(dump).eq(
                "contact_uuid", contact_uuid
            ).execute()

        message_package = {
            'messages': messages,
            'input_prompt': "temporary value",
            'state': "addition-question-sequence"
        }
    elif user_message == 'subtract':
        message_package = {
            'messages': [
                "Time for some subtraction!",
                "Type your response as a number.  For example, for '1 - 1', you'd write 0."
            ],
            'input_prompt': "Here's the first one... What's 3-1?",
            'state': "subtract-question-sequence"
        }
    elif user_message == 'exit':
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
    return message_package


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
        r = requests.post(
            f'https://whatsapp.turn.io/v1/messages',
            data=json.dumps(data),
            headers=headers
        )

    # Update the context object with the new state of the conversation
    context = {
        "context":{
            "user": whatsapp_id,
            "state": message_package['state'],
            "bot_message": message_package['input_prompt'],
            "user_message": user_message,
            "type": 'ask'
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
