import os
import json
import requests

from dotenv import load_dotenv

load_dotenv()

# os.environ.get('SUPABASE_URL')


def create_text_message(message_text, whatsapp_id):
    data = {
        "preview_url": False,
        "recipient_type": "individual",
        "to": whatsapp_id,
        "type": "text",
        "text": {
            "body": message_text
        }
    }   
    return data

def create_button_objects(button_options):
    button_arr = []
    for option in button_options:
        button_choice = {
            "type": "reply",
            "reply": {
                "id": "inquiry-yes",
                "title": "add" 
            }
        }
        button_arr.append(button_choice)
    return button_arr

def create_interactive_message(message_text, button_options, whatsapp_id):

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


def generate_message(data_json):
    """ pending

    REQUIREMENTS
    - implement logging of message
    - have a very simple activity which allows for different dialogue
      * add - Add the numbers, 1+1, 2+2
      * subtract - Subtract the numbers, 1-1, 2-2
      * menu - Choose one
    - send message data to retrieve dialogue state
    - retrieve response and build message object
    - send message object

    Need to make util functions that apply to both /nlu and /conversation_manager
    """

    message_data = data_json.get('message_data', '')
    context_data = data_json.get('context', '')
    
    whatsapp_id = message_data['message']['_vnd']['v1']['chat']['owner'].replace("+","")
    user_message = message_data['message']['text']['body']
    
    if user_message == '':
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
    else:
        message_package = {
            'messages': [
                "Hmmm...sorry friend.  I'm not really sure what to do."
            ],
            'input_prompt': "Please type add or subtract to start a math activity.",
            'state': "reprompt-menu-options"
        }

    headers = {
        'Authorization': f"Bearer {os.environ.get('TURN_AUTHENTICATION_TOKEN')}",
        'Content-Type': 'application/json'
    }

    for message in message_package['messages']:
        data = create_text_message(message, whatsapp_id)
        r = requests.post(f'https://whatsapp.turn.io/v1/messages', data=json.dumps(data), headers=headers)

    # print("==================")
    # print("Headers")
    # print(headers)
    # print("Data")
    # print(data)
    # print("Request Info")
    # print(r)
    # print("==================")


    context = {"context":{"user": whatsapp_id, "state": message_package['state'], "bot_message": message_package['input_prompt'], "user_message": user_message}}

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