import sys
import ctypes
import winreg
import shutil
import webbrowser
import uvicorn
import colorama
from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from settings import *
import web_managing
import db
import log

colorama.init(convert=True)

logger = logging.getLogger(__name__)
logging.basicConfig(level=LOGGING_LEVEL, handlers=[log.ColorHandler()] if 'PYCHARM_HOSTED' in os.environ else None)
app = FastAPI()


def check_and_create_association():
    extension = '.mionly'
    program_id = 'Zwylair.Mionly'
    description = 'Mionly Test File'
    executable_path = f'"{sys.executable}" "{__file__}"' if getattr(sys, 'frozen', True) else f'"{sys.executable}"'
    run_command = f'{executable_path} "%1"'

    try:
        command = winreg.QueryValue(winreg.HKEY_CLASSES_ROOT, f'{program_id}\\shell\\open\\command')

        if command == run_command:
            logger.info(f'Association for {extension} already exists')
            return
    except FileNotFoundError:
        logger.info(f'No association found for {extension}. Creating now...')

    try:
        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, extension) as key:
            winreg.SetValue(key, '', winreg.REG_SZ, program_id)

        with winreg.CreateKey(winreg.HKEY_CLASSES_ROOT, program_id) as key:
            winreg.SetValue(key, '', winreg.REG_SZ, description)

            with winreg.CreateKey(key, r'shell\open\command') as cmd_key:
                winreg.SetValue(cmd_key, '', winreg.REG_SZ, run_command)

        logger.info(f'Association for {extension} created successfully.')
    except Exception as e:
        logger.info(f'Failed to create association for {extension}: {e}')


@app.middleware('http')
async def disable_cache_middleware(request: Request, call_next):
    response: Response = await call_next(request)
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


if __name__ == '__main__':
    if not ctypes.windll.shell32.IsUserAnAdmin():
        logger.info('Ran not as admin, rerunning')

        arguments = [__file__] + sys.argv[1:]
        arguments = ' '.join(['"' + i + '"' for i in arguments])
        arguments = arguments if getattr(sys, 'frozen', True) else None

        ctypes.windll.shell32.ShellExecuteW(None, 'runas', sys.executable, arguments, None, 1)
        exit(0)

    logger.info('Ran as admin')

    # moving to main directory (changes when opened by test file)
    os.chdir(os.path.dirname(__file__ if getattr(sys, 'frozen', True) else sys.executable))

    shutil.rmtree(WEB_CACHE_PATH, ignore_errors=True)
    os.makedirs(WEB_CACHE_PATH, exist_ok=True)

    check_and_create_association()
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
    else:
        webbrowser.open_new('http://{}:{}/index.html'.format(HOST_URL, HOST_PORT))

    app.mount('/', StaticFiles(directory=WEB_DIR, html=True), name='web')
    uvicorn.run(app, host=HOST_URL, port=HOST_PORT)
