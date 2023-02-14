import os
import json
import requests

from dotenv import load_dotenv

load_dotenv()

# os.environ.get('SUPABASE_URL')


def create_text_message(message_text, whatsapp_id):
    """ Fills a template with the necessary information to send a text message to Whatsapp
    
    Inputs
    - message_text: str - the content that the message should display
    - whatsapp_id: str - the message recipient's phone number

    Outputs
    - message_data: dict - a preformatted template with the inputs' values included
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
    - button_arr: list - a list of button objects that use a template filled with the input values

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
    """ Fills a template with the necessary information to send a message with button options to Whatsapp

    * NOTE: Not fully implemented and tested
    * NOTE/TODO: It is possible to create other kinds of messages with the 'interactive message' template
    * Documentation: https://whatsapp.turn.io/docs/api/messages#interactive-messages

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


def return_next_conversational_state(context_data, user_message):
    """ Evaluates the current state of the conversation to determine resources for the next state of the conversation

    Input
    - context_data: dict - data about the conversation's current state received from the Turn.io stack
    - user_message: str - the message the user sent in response to the state

    Output
    - message_package: dict - a series of messages and user input to send the user
    """
    if context_data['user_message'] == '' and context_data['state'] == 'start-conversation':
            message_package = {
            'messages': [],
            'input_prompt': "Welcome to our math practice.  What would you like to try?  Type add or subtract.",
            'state': "welcome-sequence"
        }
    elif user_message == 'add':
        message_package = {
            'messages': [
                "Great, let's do some addition",
                "First, we'll start with single digits.",
                "Type your response as a number.  For example, for '1 + 1', you'd write 2."
            ],
            'input_prompt': "Here's the first one... What's 2+2?",
            'state': "add-question-sequence"
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


def manage_conversational_response(data_json):
    """ Parses message data, determines how to respond to user message at a given conversational state, builds/sends messages, and updates/sends context

    Input
    - data_json: dict - the data for a message the user sent to Turn.io/Whatsapp

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
    
    message_package = return_next_conversational_state(context_data, user_message)

    headers = {
        'Authorization': f"Bearer {os.environ.get('TURN_AUTHENTICATION_TOKEN')}",
        'Content-Type': 'application/json'
    }

    # Send all messages for the current state before a user input prompt (text/button input request)
    for message in message_package['messages']:
        data = create_text_message(message, whatsapp_id)
        r = requests.post(f'https://whatsapp.turn.io/v1/messages', data=json.dumps(data), headers=headers)

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