import requests

request = requests.post(url=
                        'https://tangibleai-mathtext-fastapi.hf.space/sentiment-analysis',
                        json={"content": "I reject it"}).json()

print(request)

request = requests.post(url=
                        'https://tangibleai-mathtext-fastapi.hf.space/text2int',
                        json={"content": "seven thousand nine hundred fifty seven"}
                        ).json()

print(request)
