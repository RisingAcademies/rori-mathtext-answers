import requests

# request = requests.post(url=
#                         'https://tangibleai-mathtext-fastapi.hf.space/sentiment-analysis',
#                         json={"content": "I reject it"}).json()

# print(request)

# request = requests.post(url=
#                         'https://tangibleai-mathtext-fastapi.hf.space/text2int',
#                         json={"content": "seven thousand nine hundred fifty seven"}
#                         ).json()

# print(request)


# # json = {
# #     'message': {
# #         '_vnd': {
# #             'v1': {
# #                 'author': {
# #                     'id': 57787919091,
# #                     'name': 'GT',
# #                     'type': 'OWNER'
# #                 },
# #                 'card_uuid': None,
# #                 'chat': {
# #                     'assigned_to': {
# #                         'id': 'jhk151kl-hj42-3752-3hjk-h4jk6hjkk2',
# #                         'name': 'Greg Thompson',
# #                         'type': 'OPERATOR'
# #                     },
# #                     'contact_uuid': 'j43hk26-2hjl-43jk-hnk2-k4ljl46j0ds09',
# #                     'inserted_at': '2022-07-05T04:00:34.033522Z',
# #                     'owner': '+57787919091',
# #                     'permalink': 'https://app.turn.io/c/4kl209sd0-a7b8-2hj3-8563-3hu4a89b32',
# #                     'state': 'OPEN',
# #                     'state_reason': 'Re-opened by inbound message.',
# #                     'unread_count': 19,
# #                     'updated_at': '2023-01-10T02:37:28.487319Z',
# #                     'uuid': '4kl209sd0-a7b8-2hj3-8563-3hu4a89b32'
# #                 },
# #                 'direction': 'inbound',
# #                 'faq_uuid': None,
# #                 'in_reply_to': None,
# #                 'inserted_at': '2023-01-10T02:37:28.477940Z',
# #                 'labels': [{
# #                     'confidence': 0.506479332,
# #                     'metadata': {
# #                         'nlu': {
# #                             'confidence': 0.506479332,
# #                             'intent': 'question',
# #                             'model_name': 'nlu-general-spacy-ngrams-20191014'
# #                         }
# #                     },
# #                     'uuid': 'ha7890s2k-hjk2-2476-s8d9-fh9779a8a9ds',
# #                     'value': 'Unclassified'
# #                 }],
# #                 'last_status': None,
# #                 'last_status_timestamp': None,
# #                 'on_fallback_channel': False,
# #                 'rendered_content': None,
# #                 'uuid': 's8df79zhws-h89s-hj23-7s8d-thb248d9bh2qn'
# #             }
# #         },
# #         'from': 57787919091,
# #         'id': 'hsjkthzZGehkzs09sijWA3',
# #         'text': {'body': 'eight'},
# #         'timestamp': 1673318248,
# #         'type': 'text'
# #     },
# #     'type': 'message'
# # }

# json = b'{"message_data": {"message":{"_vnd":{"v1":{"author":{"id":57787919091,"name":"GT","type":"OWNER"},"card_uuid":null,"chat":{"assigned_to":{"id":"jhk151kl-hj42-3752-3hjk-h4jk6hjkk2","name":"Greg Thompson","type":"OPERATOR"},"contact_uuid":"j43hk26-2hjl-43jk-hnk2-k4ljl46j0ds09","inserted_at":"2022-07-05T04:00:34.033522Z","owner":"+57787919091","permalink":"https://app.turn.io/c/4kl209sd0-a7b8-2hj3-8563-3hu4a89b32","state":"OPEN","state_reason":"Re-opened by inbound message.","unread_count":14,"updated_at":"2023-01-10T02:37:28.487319Z","uuid":"4kl209sd0-a7b8-2hj3-8563-3hu4a89b32"},"direction":"inbound","faq_uuid":null,"in_reply_to":null,"inserted_at":"2023-01-10T02:37:28.477940Z","labels":[{"confidence":0.506479332,"metadata":{"nlu":{"confidence":0.506479332,"intent":"question","model_name":"nlu-general-spacy-ngrams-20191014"}},"uuid":"ha7890s2k-hjk2-2476-s8d9-fh9779a8a9ds","value":"Unclassified"}],"last_status":null,"last_status_timestamp":null,"on_fallback_channel":false,"rendered_content":null,"uuid":"s8df79zhws-h89s-hj23-7s8d-thb248d9bh2qn"}},"from":57787919091,"id":"hsjkthzZGehkzs09sijWA3","text":{"body":"eight"},"timestamp":1673318248,"type":"text"},"type":"message"}}\n'

# # eight > 8
# request = requests.post(url=
#                         'http://localhost:7860/nlu',
#                         data=json
#                         ).json()
# print(request)

# json2 = b'{"message_data": {"message":{"_vnd":{"v1":{"author":{"id":57787919091,"name":"GT","type":"OWNER"},"card_uuid":null,"chat":{"assigned_to":{"id":"jhk151kl-hj42-3752-3hjk-h4jk6hjkk2","name":"Greg Thompson","type":"OPERATOR"},"contact_uuid":"j43hk26-2hjl-43jk-hnk2-k4ljl46j0ds09","inserted_at":"2022-07-05T04:00:34.033522Z","owner":"+57787919091","permalink":"https://app.turn.io/c/4kl209sd0-a7b8-2hj3-8563-3hu4a89b32","state":"OPEN","state_reason":"Re-opened by inbound message.","unread_count":14,"updated_at":"2023-01-10T02:37:28.487319Z","uuid":"4kl209sd0-a7b8-2hj3-8563-3hu4a89b32"},"direction":"inbound","faq_uuid":null,"in_reply_to":null,"inserted_at":"2023-01-10T02:37:28.477940Z","labels":[{"confidence":0.506479332,"metadata":{"nlu":{"confidence":0.506479332,"intent":"question","model_name":"nlu-general-spacy-ngrams-20191014"}},"uuid":"ha7890s2k-hjk2-2476-s8d9-fh9779a8a9ds","value":"Unclassified"}],"last_status":null,"last_status_timestamp":null,"on_fallback_channel":false,"rendered_content":null,"uuid":"s8df79zhws-h89s-hj23-7s8d-thb248d9bh2qn"}},"from":57787919091,"id":"hsjkthzZGehkzs09sijWA3","text":{"body":"eight, nine, ten"},"timestamp":1673318248,"type":"text"},"type":"message"}}\n'

# # "eight, nine, ten" > 8,9,10
# request = requests.post(url=
#                         'http://localhost:7860/nlu',
#                         data=json2
#                         ).json()

# print(request)


# json = b'{"message_data": {"message":{"_vnd":{"v1":{"author":{"id":57787919091,"name":"GT","type":"OWNER"},"card_uuid":null,"chat":{"assigned_to":{"id":"jhk151kl-hj42-3752-3hjk-h4jk6hjkk2","name":"Greg Thompson","type":"OPERATOR"},"contact_uuid":"j43hk26-2hjl-43jk-hnk2-k4ljl46j0ds09","inserted_at":"2022-07-05T04:00:34.033522Z","owner":"+57787919091","permalink":"https://app.turn.io/c/4kl209sd0-a7b8-2hj3-8563-3hu4a89b32","state":"OPEN","state_reason":"Re-opened by inbound message.","unread_count":14,"updated_at":"2023-01-10T02:37:28.487319Z","uuid":"4kl209sd0-a7b8-2hj3-8563-3hu4a89b32"},"direction":"inbound","faq_uuid":null,"in_reply_to":null,"inserted_at":"2023-01-10T02:37:28.477940Z","labels":[{"confidence":0.506479332,"metadata":{"nlu":{"confidence":0.506479332,"intent":"question","model_name":"nlu-general-spacy-ngrams-20191014"}},"uuid":"ha7890s2k-hjk2-2476-s8d9-fh9779a8a9ds","value":"Unclassified"}],"last_status":null,"last_status_timestamp":null,"on_fallback_channel":false,"rendered_content":null,"uuid":"s8df79zhws-h89s-hj23-7s8d-thb248d9bh2qn"}},"from":57787919091,"id":"hsjkthzZGehkzs09sijWA3","text":{"body":8},"timestamp":1673318248,"type":"text"},"type":"message"}}\n'

# # 8 > 8
# request = requests.post(url=
#                         'http://localhost:7860/nlu',
#                         data=json
#                         ).json()

# print(request)

# json = b'{"message_data": {"message":{"_vnd":{"v1":{"author":{"id":57787919091,"name":"GT","type":"OWNER"},"card_uuid":null,"chat":{"assigned_to":{"id":"jhk151kl-hj42-3752-3hjk-h4jk6hjkk2","name":"Greg Thompson","type":"OPERATOR"},"contact_uuid":"j43hk26-2hjl-43jk-hnk2-k4ljl46j0ds09","inserted_at":"2022-07-05T04:00:34.033522Z","owner":"+57787919091","permalink":"https://app.turn.io/c/4kl209sd0-a7b8-2hj3-8563-3hu4a89b32","state":"OPEN","state_reason":"Re-opened by inbound message.","unread_count":14,"updated_at":"2023-01-10T02:37:28.487319Z","uuid":"4kl209sd0-a7b8-2hj3-8563-3hu4a89b32"},"direction":"inbound","faq_uuid":null,"in_reply_to":null,"inserted_at":"2023-01-10T02:37:28.477940Z","labels":[{"confidence":0.506479332,"metadata":{"nlu":{"confidence":0.506479332,"intent":"question","model_name":"nlu-general-spacy-ngrams-20191014"}},"uuid":"ha7890s2k-hjk2-2476-s8d9-fh9779a8a9ds","value":"Unclassified"}],"last_status":null,"last_status_timestamp":null,"on_fallback_channel":false,"rendered_content":null,"uuid":"s8df79zhws-h89s-hj23-7s8d-thb248d9bh2qn"}},"from":57787919091,"id":"hsjkthzZGehkzs09sijWA3","text":{"body":"8, 9, 10"},"timestamp":1673318248,"type":"text"},"type":"message"}}\n'

# # "8, 9, 10" > "8,9,10"
# request = requests.post(url=
#                         'http://localhost:7860/nlu',
#                         data=json
#                         ).json()

# print(request)

# json = b'{"message_data": {"message":{"_vnd":{"v1":{"author":{"id":57787919091,"name":"GT","type":"OWNER"},"card_uuid":null,"chat":{"assigned_to":{"id":"jhk151kl-hj42-3752-3hjk-h4jk6hjkk2","name":"Greg Thompson","type":"OPERATOR"},"contact_uuid":"j43hk26-2hjl-43jk-hnk2-k4ljl46j0ds09","inserted_at":"2022-07-05T04:00:34.033522Z","owner":"+57787919091","permalink":"https://app.turn.io/c/4kl209sd0-a7b8-2hj3-8563-3hu4a89b32","state":"OPEN","state_reason":"Re-opened by inbound message.","unread_count":14,"updated_at":"2023-01-10T02:37:28.487319Z","uuid":"4kl209sd0-a7b8-2hj3-8563-3hu4a89b32"},"direction":"inbound","faq_uuid":null,"in_reply_to":null,"inserted_at":"2023-01-10T02:37:28.477940Z","labels":[{"confidence":0.506479332,"metadata":{"nlu":{"confidence":0.506479332,"intent":"question","model_name":"nlu-general-spacy-ngrams-20191014"}},"uuid":"ha7890s2k-hjk2-2476-s8d9-fh9779a8a9ds","value":"Unclassified"}],"last_status":null,"last_status_timestamp":null,"on_fallback_channel":false,"rendered_content":null,"uuid":"s8df79zhws-h89s-hj23-7s8d-thb248d9bh2qn"}},"from":57787919091,"id":"hsjkthzZGehkzs09sijWA3","text":{"body":"I dont know"},"timestamp":1673318248,"type":"text"},"type":"message"}}\n'

# # "8, 9, 10" > "8,9,10"
# request = requests.post(url=
#                         'http://localhost:7860/nlu',
#                         data=json
#                         ).json()

# print(request)

# json = b'{"message_data": {"message":{"_vnd":{"v1":{"author":{"id":57787919091,"name":"GT","type":"OWNER"},"card_uuid":null,"chat":{"assigned_to":{"id":"jhk151kl-hj42-3752-3hjk-h4jk6hjkk2","name":"Greg Thompson","type":"OPERATOR"},"contact_uuid":"j43hk26-2hjl-43jk-hnk2-k4ljl46j0ds09","inserted_at":"2022-07-05T04:00:34.033522Z","owner":"+57787919091","permalink":"https://app.turn.io/c/4kl209sd0-a7b8-2hj3-8563-3hu4a89b32","state":"OPEN","state_reason":"Re-opened by inbound message.","unread_count":14,"updated_at":"2023-01-10T02:37:28.487319Z","uuid":"4kl209sd0-a7b8-2hj3-8563-3hu4a89b32"},"direction":"inbound","faq_uuid":null,"in_reply_to":null,"inserted_at":"2023-01-10T02:37:28.477940Z","labels":[{"confidence":0.506479332,"metadata":{"nlu":{"confidence":0.506479332,"intent":"question","model_name":"nlu-general-spacy-ngrams-20191014"}},"uuid":"ha7890s2k-hjk2-2476-s8d9-fh9779a8a9ds","value":"Unclassified"}],"last_status":null,"last_status_timestamp":null,"on_fallback_channel":false,"rendered_content":null,"uuid":"s8df79zhws-h89s-hj23-7s8d-thb248d9bh2qn"}},"from":57787919091,"id":"hsjkthzZGehkzs09sijWA3","text":{"body":"Today is a wonderful day"},"timestamp":1673318248,"type":"text"},"type":"message"}}\n'

# # "8, 9, 10" > "8,9,10"
# request = requests.post(url=
#                         'http://localhost:7860/nlu',
#                         data=json
#                         ).json()

# print(request)


json = b'{"message_data": {"message":{"_vnd":{"v1":{"author":{"id":57787919091,"name":"GT","type":"OWNER"},"card_uuid":null,"chat":{"assigned_to":{"id":"jhk151kl-hj42-3752-3hjk-h4jk6hjkk2","name":"Greg Thompson","type":"OPERATOR"},"contact_uuid":"j43hk26-2hjl-43jk-hnk2-k4ljl46j0ds09","inserted_at":"2022-07-05T04:00:34.033522Z","owner":"+57787919091","permalink":"https://app.turn.io/c/4kl209sd0-a7b8-2hj3-8563-3hu4a89b32","state":"OPEN","state_reason":"Re-opened by inbound message.","unread_count":14,"updated_at":"2023-01-10T02:37:28.487319Z","uuid":"4kl209sd0-a7b8-2hj3-8563-3hu4a89b32"},"direction":"inbound","faq_uuid":null,"in_reply_to":null,"inserted_at":"2023-01-10T02:37:28.477940Z","labels":[{"confidence":0.506479332,"metadata":{"nlu":{"confidence":0.506479332,"intent":"question","model_name":"nlu-general-spacy-ngrams-20191014"}},"uuid":"ha7890s2k-hjk2-2476-s8d9-fh9779a8a9ds","value":"Unclassified"}],"last_status":null,"last_status_timestamp":null,"on_fallback_channel":false,"rendered_content":null,"uuid":"s8df79zhws-h89s-hj23-7s8d-thb248d9bh2qn"}},"from":57787919091,"id":"hsjkthzZGehkzs09sijWA3","text":{"body":"Today is a wonderful day"},"timestamp":1673318248,"type":"text"},"type":"message"}}\n'



request = requests.post(url=
                        'http://localhost:7860/manager',
                        data=json
                        ).json()
print(request)