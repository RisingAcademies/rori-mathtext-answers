import os
import json
import requests

from dotenv import load_dotenv

load_dotenv()

# os.environ.get('SUPABASE_URL')

def parse_data(data):
    data_bytes = requests.body
    data_decoded = data_bytes.decode()
    data_json = json.loads(data_decoded)
    return data_json

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

    # Intent Labelling #######################
    # Call to Wit.ai for intent recognition

    # message = data_json['messages'][0]['text']['body']
    # formatted_message = message.replace(' ', '%20')

    # Send a custom message with buttons
    headers = {
        'Authorization': f"Bearer {os.environ.get('TURN_AUTHENTICATION_TOKEN')}",
        'Content-Type': 'application/json'
    }
    data = {
        "to": data_json['message']['_vnd']['v1']['chat']['owner'],
        # "to": "alan",
        "type": "interactive",
        "interactive": {
            "type": "button",
            # "header": { },
            "body": {
                "text": "Did I answer your question?"
            },
            # "footer": { },
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {
                            "id": "inquiry-yes",
                            "title": "Yes" 
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "inquiry-no",
                            "title": "No" 
                        }
                    }
                ]
            }
        }
    }

    r = requests.post(f'https://whatsapp.turn.io/v1/messages', data=json.dumps(data), headers=headers)

    context = {"content":{"user":"Alan", "state": "received-and-replied-state"}}

    return context
