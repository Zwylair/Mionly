import webbrowser
from fastapi import FastAPI, Request
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
import uvicorn
from settings import *
import web_managing
import db

web_temp_dir = f'{WEB_DIR}/temp'
app = FastAPI()


@app.middleware('http')
async def disable_cache_middleware(request: Request, call_next):
    response: Response = await call_next(request)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


if __name__ == '__main__':
    db.setup(app)
    web_managing.setup(app)

    app.mount('/', StaticFiles(directory=WEB_DIR, html=True), name='web')
    webbrowser.open_new(f'http://{HOST_URL}:{HOST_PORT}/index.html')
    uvicorn.run(app, host=HOST_URL, port=HOST_PORT)
