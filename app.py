"""FastAPI endpoint
To run locally use 'uvicorn app:app --host localhost --port 7860'
"""
import re

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from mathtext.sentiment import sentiment
from mathtext.text2int import text2int
from pydantic import BaseModel

from mathtext_fastapi.nlu import prepare_message_data_for_logging
from mathtext_fastapi.conversation_manager import *

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


class Text(BaseModel):
    content: str = ""


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@app.post("/hello")
def hello(content: Text = None):
    content = {"message": f"Hello {content.content}!"}
    return JSONResponse(content=content)


@app.post("/sentiment-analysis")
def sentiment_analysis_ep(content: Text = None):
    ml_response = sentiment(content.content)
    content = {"message": ml_response}
    return JSONResponse(content=content)


@app.post("/text2int")
def text2int_ep(content: Text = None):
    ml_response = text2int(content.content)
    content = {"message": ml_response}
    return JSONResponse(content=content)


@app.post("/manager")
async def programmatic_message_manager(request: Request):
    print(request)

    data_dict = await request.json()
    # print("FULL REQUEST")
    # print(data_dict)

    # message_data = data_dict.get('message_data', '')
    # context_data = data_dict.get('context', '')

    # print("MESSAGE_DATA")
    # print(message_data)
    # print("CONTEXT_DATA")
    # print(context_data)

    context = generate_message(data_dict)
    return JSONResponse(context)

@app.post("/nlu")
async def evaluate_user_message_with_nlu_api(request: Request):
    """ Calls NLU APIs on the most recent user message from Turn.io message data and logs the message data

    Input
    - request.body: a json object of message data for the most recent user response

    Output
    - int_data_dict or sent_data_dict: A dictionary telling the type of NLU run and the resulting data
      {'type':'integer', 'data': '8'}
      {'type':'sentiment', 'data': 'negative'}
    """

    data_dict = await request.json()
    message_data = data_dict.get('message_data', '')
    message_text = message_data['message']['text']['body']

    # Handles if a student answer is already an integer or a float (ie., 8)
    if type(message_text) == int or type(message_text) == float:
        nlu_response = {'type': 'integer', 'data': message_text, 'confidence': ''}
        prepare_message_data_for_logging(message_data, nlu_response, message_data)
        return JSONResponse(content=nlu_response)

    # Removes whitespace and converts str to arr to handle multiple numbers
    message_text_arr = re.split(", |,| ", message_text.strip())

    # Handle if a student answer is a string of numbers (ie., "8,9, 10")
    if all(ele.isdigit() for ele in message_text_arr):
        nlu_response = {'type': 'integer', 'data': ','.join(message_text_arr), 'confidence': ''}
        prepare_message_data_for_logging(message_data, nlu_response, message_data)
        return JSONResponse(content=nlu_response)

    student_response_arr = []

    for student_response in message_text_arr:
        # Checks the student answer and returns an integer

        int_api_resp = text2int(student_response.lower())
        student_response_arr.append(int_api_resp)

    # '32202' is text2int's error code for non-integer student answers (ie., "I don't know")
    # If any part of the list is 32202, sentiment analysis will run
    if 32202 in student_response_arr:
        sentiment_api_resp = sentiment(message_text)
        # [{'label': 'POSITIVE', 'score': 0.991188645362854}]
        sent_data_dict = {'type': 'sentiment', 'data': sentiment_api_resp[0]['label']}
        nlu_response = {'type': 'sentiment', 'data': sentiment_api_resp[0]['label'], 'confidence': sentiment_api_resp[0]['score']}
    else:
        if len(student_response_arr) > 1:
            nlu_response = {'type': 'integer', 'data': ','.join(str(num) for num in student_response_arr), 'confidence': ''}
        else:
            nlu_response = {'type': 'integer', 'data': student_response_arr[0], 'confidence': ''}

    # Uncomment to enable logging to Supabase
    prepare_message_data_for_logging(message_data, nlu_response, message_data)
    return JSONResponse(content=nlu_response)
