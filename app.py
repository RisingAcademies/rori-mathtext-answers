"""FastAPI endpoint
To run locally use 'uvicorn app:app --host localhost --port 7860'
or
`python -m uvicorn app:app --reload --host localhost --port 7860`
"""
import asyncio
import random
import sentry_sdk

from logging import getLogger

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from mathtext_fastapi.constants import (
    APPROVED_KEYWORDS,
    ERROR_RESPONSE_DICT,
    SENTRY_DSN,
    SENTRY_PROFILES_SAMPLE_RATE,
    SENTRY_TRACES_SAMPLE_RATE,
    TIMEOUT_RESPONSE_DICT,
    TIMEOUT_THRESHOLD,
)
from mathtext_fastapi.django_logging.django_logging import (
    log_user_and_message_context,
)
from mathtext_fastapi.endpoint_utils.endpoint_utils import (
    extract_student_message,
    run_nlu_and_activity_evaluation,
)
from mathtext_fastapi.endpoint_utils.request_validators import (
    parse_nlu_api_request_for_message,
)
from mathtext_fastapi.v2_nlu import (
    run_keyword_and_intent_evaluations,
)
from mathtext.predict_intent import predict_message_intent

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


@app.get("/keywords")
def topics():
    """Return Rori's supported keywords"""
    return JSONResponse(content={"keywords": APPROVED_KEYWORDS})


@app.post("/intent-recognition")
def intent_recognition_ep(content: Text = None):
    ml_response = predict_message_intent(content.content)
    return JSONResponse(content=ml_response)


@app.post("/nlu/intent-recognition")
async def recognize_keywords_and_intents(request: Request):
    """Attempts to detect approved keywords and intents in a student message"""
    message_dict = await parse_nlu_api_request_for_message(request)
    if message_dict == ERROR_RESPONSE_DICT:
        return ERROR_RESPONSE_DICT

    message_text = await extract_student_message(message_dict)
    try:
        nlu_response = await asyncio.wait_for(
            run_keyword_and_intent_evaluations(message_text),
            TIMEOUT_THRESHOLD,
        )
    except asyncio.TimeoutError:
        nlu_response = TIMEOUT_RESPONSE_DICT
    except Exception as e:
        nlu_response = ERROR_RESPONSE_DICT
        log.error(f"NLU Intent Recognition Endpoint Exception: {e}")
    return JSONResponse(content=nlu_response)


@app.post("/v2/nlu")
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

    try:
        nlu_response, activity_session = await asyncio.wait_for(
            run_nlu_and_activity_evaluation(message_dict),
            TIMEOUT_THRESHOLD,
        )
    except asyncio.TimeoutError:
        nlu_response = TIMEOUT_RESPONSE_DICT
    except Exception as e:
        nlu_response = ERROR_RESPONSE_DICT
        log.error(f"V2 NLU Endpoint Exception: {e}")

    asyncio.create_task(
        log_user_and_message_context(message_dict, nlu_response, activity_session)
    )

    return JSONResponse(content=nlu_response)


@app.get("/progress")
async def get_user_progress(request: Request):
    num_lessons_completed = random.randint(3, 15)
    num_questions_answered = random.randint(20, 80)
    num_correct_answers = num_questions_answered - 7
    url = f"https://res.cloudinary.com/tangibleai/image/upload/co_rgb:FFFFFF,l_text:Comfortaa_160_normal_left:{num_lessons_completed}/fl_layer_apply,x_-0.28,y_-0.085/co_rgb:FFFFFF,l_text:Comfortaa_160_normal_left:{num_questions_answered}/fl_layer_apply,x_-0.035,y_-0.085/co_rgb:FFFFFF,l_text:arial_160_normal_left:{num_correct_answers}/fl_layer_apply,x_0.25,y_-0.085/rori/progress_card_for_cloudinary_numbers_only_rpmhn5.jpg"
    content = {"report_url": url}
    return JSONResponse(content=content)
