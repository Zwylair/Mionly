import shutil
import webbrowser
import uvicorn
import colorama
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


if __name__ == '__main__':
    colorama.init(convert=True)
    shutil.rmtree(WEB_CACHE_PATH, ignore_errors=True)
    os.makedirs(WEB_CACHE_PATH, exist_ok=True)

    db.setup(app)
    web_managing.setup(app)

    app.mount('/', StaticFiles(directory=WEB_DIR, html=True), name='web')
    webbrowser.open_new('http://{}:{}/index.html'.format(HOST_URL, HOST_PORT))
    uvicorn.run(app, host=HOST_URL, port=HOST_PORT)
