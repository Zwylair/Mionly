import os
import sys
import time
import typing
import subprocess
import dearpygui.dearpygui as dpg
from settings import *
import log

logger = logging.getLogger(__name__)
logging.basicConfig(level=LOGGING_LEVEL, handlers=log.get_handler_for_me())
lockfile: typing.TextIO | None = None
lockfile_path: str | None = None
main_executable: str | None = None


def setup(main_filename: str, local_lockfile_path: str):
    global lockfile, main_executable, lockfile_path

    time.sleep(1)

    lockfile_path = local_lockfile_path
    lockfile = open(lockfile_path, 'w')
    main_executable = main_filename


def stop_mionly():
    if lockfile is not None and not lockfile.closed:
        logger.debug(f'Unlocking {lockfile_path}')
        lockfile.close()
        os.remove(lockfile_path)

    logger.debug('Stopping DearPyGui')
    dpg.stop_dearpygui()


def rerun():
    stop_mionly()

    if getattr(sys, 'frozen', False):
        logger.debug('Mionly is frozen. Restart via launching exe file')
        launch_options = [sys.executable]
    else:
        logger.debug('Mionly is not frozen. Restart via launching script')
        launch_options = [sys.executable, main_executable]

    logger.debug(f'Restart command: {launch_options}')
    subprocess.run(launch_options)
