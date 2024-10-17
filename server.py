import sys
import webbrowser
import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from settings import *
import web_managing
import db

app = FastAPI()


@app.middleware('http')
async def disable_cache_middleware(request: Request, call_next):
    response: Response = await call_next(request)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


db.setup(app)
web_managing.setup(app)

if len(sys.argv[1:]) > 0:
    round_link = web_managing.start_test(
        web_managing.ChosenTest(
            name=sys.argv[1],
            randomize_rounds=True,
            randomize_answers=True
        )
    )
    webbrowser.open_new('http://{}:{}{}'.format(HOST_URL, HOST_PORT, round_link))

app.mount('/', StaticFiles(directory=WEB_DIR, html=True), name=WEB_DIR)
uvicorn.run(app, host=HOST_URL, port=HOST_PORT, use_colors=getattr(sys, 'frozen', False))
