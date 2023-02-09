import os
import json
import requests

from dotenv import load_dotenv

load_dotenv()

# os.environ.get('SUPABASE_URL')


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

    whatsapp_id = data_json['message']['_vnd']['v1']['chat']['owner'].replace("+","")

    print("DATA JSON")
    print(data_json)

    user_message = data_json['message']['text']['body']

    if user_message == 'add':
        data = {
            "preview_url": False,
            "recipient_type": "individual",
            "to": whatsapp_id,
            "type": "text",
            "text": {
                "body": "What's 2+2?"
            }
        }
    elif user_message == 'substract':
        data = {
            "preview_url": False,
            "recipient_type": "individual",
            "to": whatsapp_id,
            "type": "text",
            "text": {
                "body": "What's 1-1?"
            }
        }    
    else:
        data = {
        "to": whatsapp_id,
        # "to": "alan",
        "type": "interactive",
        "interactive": {
            "type": "button",
            # "header": { },
            "body": {
                "text": "Please choose one of the following options."
            },
            # "footer": { },
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {
                            "id": "inquiry-yes",
                            "title": "add" 
                        }
                    },
                    {
                        "type": "reply",
                        "reply": {
                            "id": "inquiry-no",
                            "title": "subtract" 
                        }
                    }
                ]
            }
        }
    }


    # data = {
    #     "to": whatsapp_id,
    #     # "to": "alan",
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

    r = requests.post(f'https://whatsapp.turn.io/v1/messages', data=json.dumps(data), headers=headers)
    print("==================")
    print("Headers")
    print(headers)
    print("Data")
    print(data)
    print("Request Info")
    print(r)
    print("--")
    # print(r.body)
    print("==================")


    context = {"content":{"user":"Alan", "state": "received-and-replied-state"}}

    return context
