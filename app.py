"""FastAPI endpoint
To run locally use 'uvicorn app:app --host localhost --port 7860'
"""
import ast
import scripts.quiz.generators as generators
import scripts.quiz.hints as hints
import scripts.quiz.questions as questions
import scripts.quiz.utils as utils

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
    

@app.post("/start")
async def ask_math_question(request: Request):
    """Generate a question data
    
    Input
    {
        'difficulty': 0.1,
        'do_increase': True | False
    }

    Output
    {
        'text': 'What is 1+2?',
        'difficulty': 0.2,
        'question_numbers': [3, 1, 4]
    }
    """
    data_dict = await request.json()
    message_data = ast.literal_eval(data_dict.get('message_data', '').get('message_body', ''))
    difficulty = message_data['difficulty']
    do_increase = message_data['do_increase']

    return JSONResponse(generators.start_interactive_math(difficulty, do_increase))


@app.post("/hint")
async def get_hint(request: Request):
    """Generate a hint data
    
    Input
    {
        'start': 5,
        'step': 1,
        'difficulty': 0.1
    }

    Output
    {
        'text': 'What number is greater than 4 and less than 6?',
        'difficulty': 0.1,
        'question_numbers': [5, 1, 6]
    }
    """
    data_dict = await request.json()
    message_data = ast.literal_eval(data_dict.get('message_data', '').get('message_body', ''))
    start = message_data['start']
    step = message_data['step']
    difficulty = message_data['difficulty']

    return JSONResponse(hints.generate_hint(start, step, difficulty))


@app.post("/question")
async def ask_math_question(request: Request):
    """Generate a question data
    
    Input
    {
        'start': 5,
        'step': 1,
        'question_num': 1  # optional
    }

    Output
    {
        'question': 'What is 1+2?',
        'start': 5,
        'step': 1,
        'answer': 6
    }
    """
    data_dict = await request.json()
    message_data = ast.literal_eval(data_dict.get('message_data', '').get('message_body', ''))
    start = message_data['start']
    step = message_data['step']
    arg_tuple = (start, step)
    try:
        question_num = message_data['question_num']
        arg_tuple += (question_num,)
    except KeyError:
        pass

    return JSONResponse(questions.generate_question_data(*arg_tuple))


@app.post("/difficulty")
async def get_hint(request: Request):
    """Generate a number matching difficulty
    
    Input
    {
        'difficulty': 0.01,
        'do_increase': True
    }

    Output - value from 0.01 to 0.99 inclusively:
    0.09
    """
    data_dict = await request.json()
    message_data = ast.literal_eval(data_dict.get('message_data', '').get('message_body', ''))
    difficulty = message_data['difficulty']
    do_increase = message_data['do_increase']

    return JSONResponse(utils.get_next_difficulty(difficulty, do_increase))


@app.post("/start_step")
async def get_hint(request: Request):
    """Generate a start and step values
    
    Input
    {
        'difficulty': 0.01,
        'path_to_csv_file': 'scripts/quiz/data.csv'  # optional
    }

    Output - tuple (start, step):
    (5, 1)
    """
    data_dict = await request.json()
    message_data = ast.literal_eval(data_dict.get('message_data', '').get('message_body', ''))
    difficulty = message_data['difficulty']
    arg_tuple = (difficulty,)
    try:
        path_to_csv_file = message_data['path_to_csv_file']
        arg_tuple += (path_to_csv_file,)
    except KeyError:
        pass

    return JSONResponse(utils.get_next_difficulty(*arg_tuple))


@app.post("/sequence")
async def generate_question(request: Request):
    """Generate a sequence from start, step and optional separator parameter
    
    Input
    {
        'start': 5,
        'step': 1,
        'sep': ', '  # optional
    }

    Output
    5, 6, 7
    """
    data_dict = await request.json()
    message_data = ast.literal_eval(data_dict.get('message_data', '').get('message_body', ''))
    start = message_data['start']
    step = message_data['step']
    arg_tuple = (start, step)
    try:
        sep = message_data['sep']
        arg_tuple += (sep,)
    except KeyError:
        pass

    return JSONResponse(utils.convert_sequence_to_string(*arg_tuple))
