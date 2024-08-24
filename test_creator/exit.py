import os
import sys
import signal
import typing
import subprocess
import dearpygui.dearpygui as dpg
from settings import *
import log

logger = logging.getLogger(__name__)
logging.basicConfig(level=LOGGING_LEVEL, handlers=log.get_handler_for_me())
lockfile: typing.TextIO | None = None
main_executable: str | None = None


def stop_mionly():
    if not lockfile.closed:
        logger.debug(f'Unlocking {TEST_CREATOR_LOCK_FILENAME}')

        lockfile.close()
        os.remove(TEST_CREATOR_LOCK_FILENAME)

    logger.debug('Stopping DearPyGui')
    dpg.stop_dearpygui()


def exit_app():
    os.kill(os.getpid(), signal.SIGINT)


def rerun():
    stop_mionly()

    if getattr(sys, 'frozen', False):
        # not works in frozen console version

        logger.debug('Mionly is frozen. Restart via launching exe file')
        logger.debug(f'Restart command: "{sys.executable}"')
        subprocess.Popen(
            sys.executable,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    else:
        logger.debug('Mionly is not frozen. Restart via launching script')
        logger.debug(f'Restart command: "{sys.executable}" "{main_executable}"')
        subprocess.Popen(
            [sys.executable, main_executable],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
