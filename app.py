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

from mathtext_fastapi.logging import prepare_message_data_for_logging
from mathtext_fastapi.conversation_manager import manage_conversational_response
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
    Calls the conversation management function to determine what to send to the user based on the current state and user response

    Input
    request.body: dict - a json object of message data for the most recent user response
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
    context: dict - a json object that holds the information for the current state
    {
        "user": "47897891", 
        "state": "welcome-message-state", 
        "bot_message": "Welcome to Rori!", 
        "user_message": "", 
        "type": "ask"
    }
    """
    data_dict = await request.json()
    context = manage_conversational_response(data_dict)
    return JSONResponse(context)


@app.post("/nlu")
async def evaluate_user_message_with_nlu_api(request: Request):
    """ Calls the nlu evaluation function to run nlu functions and returns the nlu_response to Turn.io

    Input
    - request.body: a json object of message data for the most recent user response

    Output
    - int_data_dict or sent_data_dict: A dictionary telling the type of NLU run and the resulting data
      {'type':'integer', 'data': '8'}
      {'type':'sentiment', 'data': 'negative'}
    """
    data_dict = await request.json()
    message_data = data_dict.get('message_data', '')
    nlu_response = evaluate_message_with_nlu(message_data)
    return JSONResponse(content=nlu_response)
