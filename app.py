"""FastAPI endpoint
To run locally use 'uvicorn app:app --host localhost --port 7860'
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from modules.sentiment import sentiment
from modules.text2int import text2int
from modules.nlu import prepare_message_data_for_logging
# FIXME:
# from mathtext.text2int import text2int

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
    message_text = message_data['message']['text']['body'].lower()

    int_api_resp = text2int(message_text)

    if int_api_resp == '32202':
        sentiment_api_resp = sentiment(message_text)
        # [{'label': 'POSITIVE', 'score': 0.991188645362854}]
        sent_data_dict = {'type': 'sentiment', 'data': sentiment_api_resp[0]['label']}
        return JSONResponse(content={'type': 'sentiment', 'data': 'negative'})

    prepare_message_data_for_logging(message_data)

    int_data_dict = {'type': 'integer', 'data': int_api_resp}
    return JSONResponse(content=int_data_dict)

