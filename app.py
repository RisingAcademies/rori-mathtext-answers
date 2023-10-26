"""FastAPI endpoint
To run locally use 'uvicorn app:app --host localhost --port 7860'
or
`python -m uvicorn app:app --reload --host localhost --port 7860`
"""
import asyncio
import ast

# import datetime as dt
import sentry_sdk

# from collections.abc import Mapping
# from dateutil.parser import isoparse
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# from json import JSONDecodeError
from logging import getLogger
from pydantic import BaseModel

from mathtext.predict_intent import predict_message_intent
from mathtext_fastapi.constants import (
    ERROR_RESPONSE_DICT,
    SENTRY_DSN,
    SENTRY_PROFILES_SAMPLE_RATE,
    SENTRY_TRACES_SAMPLE_RATE,
    TIMEOUT_RESPONSE_DICT,
    TIMEOUT_THRESHOLD,
)

# Temporary comment to trigger rebuild

# TODO: Simplify conversation_manager code
from mathtext_fastapi.nlu import (
    evaluate_message_with_nlu,
    run_keyword_evaluation,
)
from mathtext_fastapi.supabase_logging_async import prepare_message_data_for_logging
from mathtext_fastapi.request_validators import (
    truncate_long_message_text,
    parse_nlu_api_request_for_message,
)
from mathtext_fastapi.v2_nlu import (
    v2_evaluate_message_with_nlu,
    run_keyword_and_intent_evaluations,
)


log = getLogger(__name__)

sentry_sdk.init(
    dsn=SENTRY_DSN,
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    # We recommend adjusting this value in production,
    traces_sample_rate=SENTRY_TRACES_SAMPLE_RATE,
    profiles_sample_rate=SENTRY_PROFILES_SAMPLE_RATE,
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
    # ml_response = text2int(content.content)
    # content = {"message": ml_response}
    # return JSONResponse(content=content)
    return JSONResponse(content={})


@app.post("/keyword-detection")
def keyword_detection_ep(content: Text = None):
    ml_response = run_keyword_evaluation(content.content)
    content = {"content": ml_response}
    return JSONResponse(content=content)


@app.post("/intent-recognition")
def intent_recognition_ep(content: Text = None):
    ml_response = predict_message_intent(content.content)
    # content = {"content": ml_response}
    return JSONResponse(content=ml_response)


@app.post("/nlu/intent-recognition")
async def recognize_keywords_and_intents(request: Request):
    """Attempts to detect approved keywords and intents in a student message"""
    message_dict = await parse_nlu_api_request_for_message(request)
    if message_dict == ERROR_RESPONSE_DICT:
        return ERROR_RESPONSE_DICT

    message_text = str(message_dict.get("message_body", ""))
    message_text = truncate_long_message_text(message_text)

    try:
        nlu_response = await asyncio.wait_for(
            run_keyword_and_intent_evaluations(message_text),
            TIMEOUT_THRESHOLD,
        )
    except asyncio.TimeoutError:
        nlu_response = TIMEOUT_RESPONSE_DICT
    return nlu_response


@app.post("/nlu")
async def evaluate_user_message_with_nlu_api(request: Request):
    """Calls nlu evaluation and returns the nlu_response

    Input
    - request.body: json - message data for the most recent user response

    Output
    - int_data_dict or sent_data_dict: dict - the type of NLU run and result
      {'type':'integer', 'data': '8', 'confidence': 0}
    """
    message_dict = await parse_nlu_api_request_for_message(request)
    if message_dict == ERROR_RESPONSE_DICT:
        return ERROR_RESPONSE_DICT

    message_text = str(message_dict.get("message_body", ""))
    message_text = truncate_long_message_text(message_text)
    expected_answer = str(message_dict.get("expected_answer", ""))

    try:
        nlu_response = await asyncio.wait_for(
            evaluate_message_with_nlu(message_text, expected_answer), TIMEOUT_THRESHOLD
        )
    except asyncio.TimeoutError:
        nlu_response = TIMEOUT_RESPONSE_DICT

    asyncio.create_task(prepare_message_data_for_logging(message_dict, nlu_response))

    return JSONResponse(content=nlu_response)


@app.post("/v2/nlu")
# @app.post("/nlu")
async def v2_evaluate_user_message_with_nlu_api(request: Request):
    """Calls nlu evaluation and returns the nlu_response

    Input
    - request.body: json - message data for the most recent user response

    Output
    - int_data_dict or sent_data_dict: dict - the type of NLU run and result
    """
    message_dict = await parse_nlu_api_request_for_message(request)
    if message_dict == ERROR_RESPONSE_DICT:
        return ERROR_RESPONSE_DICT

    message_text = str(message_dict.get("message_body", ""))
    message_text = truncate_long_message_text(message_text)
    expected_answer = str(message_dict.get("expected_answer", ""))

    try:
        nlu_response = await asyncio.wait_for(
            v2_evaluate_message_with_nlu(message_text, expected_answer),
            TIMEOUT_THRESHOLD,
        )
    except asyncio.TimeoutError:
        nlu_response = TIMEOUT_RESPONSE_DICT

    asyncio.create_task(prepare_message_data_for_logging(message_dict, nlu_response))

    return JSONResponse(content=nlu_response)
