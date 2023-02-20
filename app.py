"""FastAPI endpoint
To run locally use 'uvicorn app:app --host localhost --port 7860'
"""
import ast
import re

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from mathtext.sentiment import sentiment
from mathtext.text2int import text2int
from pydantic import BaseModel

from mathtext_fastapi.logging import prepare_message_data_for_logging
from mathtext_fastapi.conversation_manager import manage_conversation_response
from mathtext_fastapi.nlu import evaluate_message_with_nlu
from scripts.quiz.generators import start_interactive_math
from scripts.quiz.hints import generate_hint

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
    """
    Calls conversation management function to determine the next state

    Input
    request.body: dict - message data for the most recent user response
    {
        "author_id": "+47897891",
        "contact_uuid": "j43hk26-2hjl-43jk-hnk2-k4ljl46j0ds09",
        "author_type": "OWNER",
        "message_body": "a test message",
        "message_direction": "inbound",
        "message_id": "ABJAK64jlk3-agjkl2QHFAFH",
        "message_inserted_at": "2022-07-05T04:00:34.03352Z",
        "message_updated_at": "2023-02-14T03:54:19.342950Z",
    }

    Output
    context: dict - the information for the current state
    {
        "user": "47897891",
        "state": "welcome-message-state",
        "bot_message": "Welcome to Rori!",
        "user_message": "",
        "type": "ask"
    }
    """
    data_dict = await request.json()
    context = manage_conversation_response(data_dict)
    return JSONResponse(context)


@app.post("/nlu")
async def evaluate_user_message_with_nlu_api(request: Request):
    """ Calls nlu evaluation and returns the nlu_response

    Input
    - request.body: json - message data for the most recent user response

    Output
    - int_data_dict or sent_data_dict: dict - the type of NLU run and result
      {'type':'integer', 'data': '8'}
      {'type':'sentiment', 'data': 'negative'}
    """
    data_dict = await request.json()
    message_data = data_dict.get('message_data', '')
    nlu_response = evaluate_message_with_nlu(message_data)
    return JSONResponse(content=nlu_response)


@app.post("/question")
async def ask_math_question(request: Request):
    """Generates a question and returns it as response along with question data
    
    Input
    request.body: json - amount of correct and incorrect answers in the account
    {
        'number_correct': 0,
        'number_incorrect': 0
    }

    Output
    context: dict - the information for the current state
    {
        'text': 'What is 1+2?',
        'question_numbers': [1,2,3,4], #3 or 4 numbers
        'right_answer': 3,
        'number_correct': 0,
        'number_incorrect': 0,
        'hints_used': 0
    }
    """
    data_dict = await request.json()
    message_data = ast.literal_eval(data_dict.get('message_data', '').get('message_body', ''))
    number_correct = message_data['number_correct']
    number_incorrect = message_data['number_incorrect']

    return JSONResponse(start_interactive_math(number_correct, number_incorrect))


@app.post("/hint")
async def get_hint(request: Request):
    """Generates a hint and returns it as response along with hint data
    
    Input
    request.body: json - amount of correct and incorrect answers in the account
    {
        'question_numbers': [1,2,3,4], # 3 or 4 numbers
        'right_answer': 3,
        'user_answer': 10,
        'number_correct': 0,
        'number_incorrect': 0,
        'hints_used': 0
    }

    Output
    context: dict - the information for the current state
    {
        'text': 'What is 1+2?',
        'question_numbers': [1,2,3], #3 or 4 numbers
        'right_answer': 3,
        'number_correct': 0,
        'number_incorrect': 0,
        'hints_used': 0
    }
    """
    data_dict = await request.json()
    message_data = ast.literal_eval(data_dict.get('message_data', '').get('message_body', ''))
    question_numbers = message_data['number_correct']
    question_numbers = message_data['number_correct']
    number_correct = message_data['number_correct']
    number_incorrect = message_data['number_incorrect']
    hints_used = message_data['hints_used']

    return JSONResponse(generate_hint(question_numbers, number_correct, number_incorrect, hints_used))
