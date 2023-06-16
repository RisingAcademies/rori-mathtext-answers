"""FastAPI endpoint
To run locally use 'uvicorn app:app --host localhost --port 7860'
or
`python -m uvicorn app:app --reload --host localhost --port 7860`
"""
import asyncio
import ast
import datetime as dt
from dateutil.parser import isoparse
from collections.abc import Mapping
import json
from json import JSONDecodeError
from logging import getLogger
import os
import sentry_sdk

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

import mathactive.microlessons.num_one as num_one_quiz
from mathtext.predict_intent import predict_message_intent
from mathtext.text2int import text2int
from mathtext.text2int import TOKENS2INT_ERROR_INT
from mathtext_fastapi.constants import SENTRY_DSN, SENTRY_TRACES_SAMPLE_RATE, SENTRY_PROFILES_SAMPLE_RATE, TIMEOUT_THRESHOLD
from mathtext_fastapi.conversation_manager import manage_conversation_response
from mathtext_fastapi.nlu import evaluate_message_with_nlu, run_keyword_evaluation
from mathtext_fastapi.supabase_logging_async import prepare_message_data_for_logging
from mathtext_fastapi.v2_conversation_manager import manage_conversation_response


ERROR_RESPONSE_DICT = {'type': 'error', 'data': TOKENS2INT_ERROR_INT, 'confidence': 0}

log = getLogger(__name__)

sentry_sdk.init(
    dsn=SENTRY_DSN,

    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production,
    traces_sample_rate=SENTRY_TRACES_SAMPLE_RATE,
    profiles_sample_rate=SENTRY_PROFILES_SAMPLE_RATE
)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")


class Text(BaseModel):
    content: str = ""


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@app.get("/sentry-debug")
async def trigger_error():
    division_by_zero = 1 / 0


@app.post("/hello")
def hello(content: Text = None):
    content = {"message": f"Hello {content.content}!"}
    return JSONResponse(content=content)


@app.post("/text2int")
def text2int_ep(content: Text = None):
    ml_response = text2int(content.content)
    content = {"message": ml_response}
    return JSONResponse(content=content)


@app.post("/v1/manager")
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


@app.post("/v2/manager")
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


@app.post("/keyword-detection")
def keyword_detection_ep(content: Text = None):
    ml_response = run_keyword_evaluation(content.content)
    content = {"content": ml_response}
    return JSONResponse(content=content)


@app.post("/intent-recognition")
def intent_recognition_ep(content: Text = None):
    ml_response = predict_message_intent(content.content)
    content = {"content": ml_response}
    return JSONResponse(content=content)


PAYLOAD_VALUE_TYPES = {
    'author_id': str,
    'author_type': str,
    'contact_uuid': str,
    'message_body': str,
    'message_direction': str,
    'message_id': str,
    'message_inserted_at': str,
    'message_updated_at': str,
    }


def payload_is_valid(payload_object):
    """
    >>> payload_is_valid({'author_id': '+5555555', 'author_type': 'OWNER', 'contact_uuid': '3246-43ad-faf7qw-zsdhg-dgGdg', 'message_body': 'thirty one', 'message_direction': 'inbound', 'message_id': 'SDFGGwafada-DFASHA4aDGA', 'message_inserted_at': '2022-07-05T04:00:34.03352Z', 'message_updated_at': '2023-04-06T10:08:23.745072Z'})
    True

    >>> payload_is_valid({"author_id": "@event.message._vnd.v1.chat.owner", "author_type": "@event.message._vnd.v1.author.type", "contact_uuid": "@event.message._vnd.v1.chat.contact_uuid", "message_body": "@event.message.text.body", "message_direction": "@event.message._vnd.v1.direction", "message_id": "@event.message.id", "message_inserted_at": "@event.message._vnd.v1.chat.inserted_at", "message_updated_at": "@event.message._vnd.v1.chat.updated_at"})
    False
    """
    try:
        isinstance(
            isoparse(payload_object.get('message_inserted_at', '')),
            dt.datetime
        )
        isinstance(
            isoparse(payload_object.get('message_updated_at', '')),
            dt.datetime
        )
    except ValueError:
        return False
    return (
        isinstance(payload_object, Mapping) and
        isinstance(payload_object.get('author_id'), str) and
        isinstance(payload_object.get('author_type'), str) and
        isinstance(payload_object.get('contact_uuid'), str) and
        isinstance(payload_object.get('message_body'), str) and
        isinstance(payload_object.get('message_direction'), str) and
        isinstance(payload_object.get('message_id'), str) and
        isinstance(payload_object.get('message_inserted_at'), str) and
        isinstance(payload_object.get('message_updated_at'), str)
    )


def log_payload_errors(payload_object):
    errors = []
    try:
        assert isinstance(payload_object, Mapping)
    except Exception as e:
        log.error(f'Invalid HTTP request payload object: {e}')
        errors.append(e)
    for k, typ in PAYLOAD_VALUE_TYPES.items():
        try:
            assert isinstance(payload_object.get(k), typ)
        except Exception as e:
            log.error(f'Invalid HTTP request payload object: {e}')
            errors.append(e)
    try:
        assert isinstance(
            dt.datetime.fromisoformat(
                payload_object.get('message_inserted_at')
            ),
            dt.datetime
        )
    except Exception as e:
        log.error(f'Invalid HTTP request payload object: {e}')
        errors.append(e)
    try:
        isinstance(
            dt.datetime.fromisoformat(
                payload_object.get('message_updated_at')
            ),
            dt.datetime
        )
    except Exception as e:
        log.error(f'Invalid HTTP request payload object: {e}')
        errors.append(e)
    return errors


def truncate_long_message_text(message_text):
    return message_text[0:100]


@app.post("/nlu")
async def evaluate_user_message_with_nlu_api(request: Request):
    """ Calls nlu evaluation and returns the nlu_response

    Input
    - request.body: json - message data for the most recent user response

    Output
    - int_data_dict or sent_data_dict: dict - the type of NLU run and result
      {'type':'integer', 'data': '8', 'confidence': 0}
    """
    log.info(f'Received request: {request}')
    log.info(f'Request header: {request.headers}')
    request_body = await request.body()
    log.info(f'Request body: {request_body}')

    await asyncio.sleep(30)

    try:
        payload = await request.json()
    except JSONDecodeError as e:
        log.error(f'JSONDecodeError: {e}')
        log.error(f'Request.json failed: {dir(request)}')
        payload = {}
    message_dict = payload.get('message_data')
    log.info(f'Request json: {payload}')

    if not message_dict:
        log.error(f'Payload: {payload}')
        message_dict = payload.get('message', {})

    if not payload_is_valid(message_dict):
        log_payload_errors(message_dict)
        return ERROR_RESPONSE_DICT

    message_text = str(message_dict.get('message_body', ''))
    message_text = truncate_long_message_text(message_text)
    expected_answer = str(message_dict.get('expected_answer', ''))

    # if expected_answer.lower().strip() == message_text.lower().strip():
    #     result = {'type': 'comparison', 'data': expected_answer, 'confidence': 1}
    #     nlu_response = result | {'intents': [result, result, result]}
    # else:
    #     timeout = TIMEOUT_THRESHOLD
    #     try:
    #         nlu_response = await asyncio.wait_for(
    #             evaluate_message_with_nlu(message_text, expected_answer), timeout
    #         )
    #     except asyncio.TimeoutError:
    #         result = {'type': 'timeout', 'data': 32202, 'confidence': 0}
    #         nlu_response = result | {'intents': [result, result, result]}

    timeout = TIMEOUT_THRESHOLD
    try:
        nlu_response = await asyncio.wait_for(
            evaluate_message_with_nlu(message_text, expected_answer),
            timeout
        )
    except asyncio.TimeoutError:
        result = {'type': 'timeout', 'data': 32202, 'confidence': 0}
        nlu_response = result | {'intents': [result, result, result]}

    asyncio.create_task(prepare_message_data_for_logging(message_dict, nlu_response))

    return JSONResponse(content=nlu_response)


@app.post("/num_one")
async def num_one(request: Request):
    """
    Input:
    {
        "user_id": 1,
        "message_text": 5,
    }
    Output:
    {
        'messages':
            ["Let's", 'practice', 'counting', '', '', '46...', '47...', '48...', '49', '', '', 'After', '49,', 'what', 'is', 'the', 'next', 'number', 'you', 'will', 'count?\n46,', '47,', '48,', '49'],
        'input_prompt': '50',
        'state': 'question'
    }
    """
    data_dict = await request.json()
    message_data = ast.literal_eval(
        data_dict.get('message_data', '').get('message_body', '')
    )
    user_id = message_data['user_id']
    message_text = message_data['message_text']
    return num_one_quiz.process_user_message(user_id, message_text)


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
    message_data = ast.literal_eval(
        data_dict.get('message_data', '').get('message_body', '')
    )
    difficulty = message_data['difficulty']
    do_increase = message_data['do_increase']

    return JSONResponse(
        generators.start_interactive_math(difficulty, do_increase)
    )


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
    message_data = ast.literal_eval(
        data_dict.get('message_data', '').get('message_body', '')
    )
    start = message_data['start']
    step = message_data['step']
    difficulty = message_data['difficulty']

    return JSONResponse(
        hints.generate_hint(start, step, difficulty)
    )


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
    message_data = ast.literal_eval(
        data_dict.get('message_data', '').get('message_body', '')
    )
    start = message_data['start']
    step = message_data['step']
    arg_tuple = (start, step)
    try:
        question_num = message_data['question_num']
        arg_tuple += (question_num,)
    except KeyError:
        pass

    return JSONResponse(
        questions.generate_question_data(*arg_tuple)
    )


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
    message_data = ast.literal_eval(
        data_dict.get('message_data', '').get('message_body', '')
    )
    difficulty = message_data['difficulty']
    do_increase = message_data['do_increase']

    return JSONResponse(
        utils.get_next_difficulty(difficulty, do_increase)
    )


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
    message_data = ast.literal_eval(
        data_dict.get('message_data', '').get('message_body', '')
    )
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
    message_data = ast.literal_eval(
        data_dict.get('message_data', '').get('message_body', '')
    )
    start = message_data['start']
    step = message_data['step']
    arg_tuple = (start, step)
    try:
        sep = message_data['sep']
        arg_tuple += (sep,)
    except KeyError:
        pass

    return JSONResponse(utils.convert_sequence_to_string(*arg_tuple))
