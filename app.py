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

# from mathtext_fastapi.logging import prepare_message_data_for_logging
# from mathtext_fastapi.conversation_manager import manage_conversation_response
# from mathtext_fastapi.nlu import evaluate_message_with_nlu

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
    """Generate a question and return it as response along with question data
    
    Input
    request.body: json - amount of correct and incorrect answers in the account
    {
        'number_correct': 0,
        'number_incorrect': 0,
        'level': 'easy'
    }

    Output
    context: dict - the information for the current state
    {
        'text': 'What is 1+2?',
        'question_numbers': [1,2,3], #3 numbers - current number, ordinal number, times
        'right_answer': 3,
        'number_correct': 0,
        'number_incorrect': 0,
        'hints_used': 0
    }
    """
    data_dict = await request.json()
    message_data = ast.literal_eval(data_dict.get('message_data', '').get('message_body', ''))
    right_answers = message_data['number_correct']
    wrong_answers = message_data['number_incorrect']
    level = message_data['level']

    return JSONResponse(generators.start_interactive_math(right_answers, wrong_answers, level))


@app.post("/hint")
async def get_hint(request: Request):
    """Generate a hint and return it as response along with hint data
    
    Input
    request.body:
    {
        'question_numbers': [1,2,3], #3 numbers - current number, ordinal number, times
        'right_answer': 3,
        'number_correct': 0,
        'number_incorrect': 0,
        'level': 'easy',
        'hints_used': 0
    }

    Output
    context: dict - the information for the current state
    {
        'text': 'What is 1+2?',
        'question_numbers': [1,2,3], #2 or 3 numbers
        'right_answer': 3,
        'number_correct': 0,
        'number_incorrect': 0,
        'level': 'easy',
        'hints_used': 0
    }
    """
    data_dict = await request.json()
    message_data = ast.literal_eval(data_dict.get('message_data', '').get('message_body', ''))
    question_numbers = message_data['question_numbers']
    right_answer = message_data['right_answer']
    number_correct = message_data['number_correct']
    number_incorrect = message_data['number_incorrect']
    level = message_data['level']
    hints_used = message_data['hints_used']

    return JSONResponse(hints.generate_hint(question_numbers, right_answer, number_correct, number_incorrect, level, hints_used))


@app.post("/generate_question")
async def generate_question(request: Request):
    """Generate a bare question and return it as response
    
    Input
    request.body: json - level
    {
        'level': 'easy'
    }

    Output
    context: dict - the information for the current state
    {
        "question": "Let's count up by 2s. What number is next if we start from 10?
        6 8 10 ..."
    }
    """
    data_dict = await request.json()
    message_data = ast.literal_eval(data_dict.get('message_data', '').get('message_body', ''))
    level = message_data['level']

    return JSONResponse(questions.generate_question_data(level)['question'])


@app.post("/numbers_by_level")
async def get_numbers_by_level(request: Request):
    """Generate three numbers and return them as response
    
    Input
    request.body: json - level
    {
        'level': 'easy'
    }

    Output
    context: dict - three generated numbers for specified level
    {
        "current_number": 10,
        "ordinal_number": 2,
        "times": 1
    }
    """
    data_dict = await request.json()
    message_data = ast.literal_eval(data_dict.get('message_data', '').get('message_body', ''))
    level = message_data['level']
    return JSONResponse(questions.generate_numbers_by_level(level))


@app.post("/number_sequence")
async def get_number_sequence(request: Request):
    """Generate a number sequence
    
    Input
    request.body: json - level
    {
        "current_number": 10,
        "ordinal_number": 2,
        "times": 1
    }

    Output
    one of following strings with (numbers differ):
    ... 1 2 3
    1 2 3 ...
    """
    data_dict = await request.json()
    message_data = ast.literal_eval(data_dict.get('message_data', '').get('message_body', ''))
    cur_num = message_data['current_number']
    ord_num = message_data['ordinal_number']
    times = message_data['times']
    return JSONResponse(questions.generate_number_sequence(cur_num, ord_num, times))


@app.post("/level")
async def get_next_level(request: Request):
    """Depending on current level and desire to level up/down return next level
    
    Input
    request.body: json - level
    {
        "current_level": "easy",
        "level_up": True
    }

    Output
    Literal - "easy", "medium" or "hard"
    """
    data_dict = await request.json()
    message_data = ast.literal_eval(data_dict.get('message_data', '').get('message_body', ''))
    cur_level = message_data['current_level']
    level_up = message_data['level_up']
    return JSONResponse(utils.get_next_level(cur_level, level_up))


@app.post("/score")
async def get_next_level(request: Request):
    """Depending on current level and desire to level up/down return next level
    
    Input
    request.body: json - score argument with value from 0 to 1
    {
        "score": 0.1
    }

    Output
    number in range 1-495
    """
    data_dict = await request.json()
    message_data = ast.literal_eval(data_dict.get('message_data', '').get('message_body', ''))
    score = message_data['score']
    return JSONResponse(questions.generate_start_by_score(score))


@app.post("/question_new")
async def get_next_level(request: Request):
    """Depending on current level and desire to level up/down return next level
    
    Input
    request.body: json - score argument with value from 0 to 1
    {
        "score": 0.1
    }

    Output
    number in range 1-495
    """
    data_dict = await request.json()
    message_data = ast.literal_eval(data_dict.get('message_data', '').get('message_body', ''))
    start = message_data.get('start', "")
    start = int(start) if start else start
    step = message_data.get('step', "")
    step = int(step) if step else step
    sequence = message_data.get('sequence', "")
    question_num = message_data.get('question_num', "")
    question_num = int(question_num) if question_num else question_num
    return JSONResponse(questions.generate_question(start, step=step, seq=sequence, question_num=question_num))
