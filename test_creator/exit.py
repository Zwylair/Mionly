import os
import signal
import typing
import dearpygui.dearpygui as dpg
from settings import *
import log

logger = logging.getLogger(__name__)
logging.basicConfig(level=LOGGING_LEVEL, handlers=[log.ColorHandler()])
lockfile: typing.TextIO | None = None


def stop_mionly(do_exit: bool = False):
    if not lockfile.closed:
        logger.debug(f'Unlocking {TEST_CREATOR_LOCK_FILENAME}')

        lockfile.close()
        os.remove(TEST_CREATOR_LOCK_FILENAME)

    logger.debug('Stopping DearPyGui')
    dpg.stop_dearpygui()

    if do_exit:
        exit_app()


def exit_app():
    os.kill(os.getpid(), signal.SIGINT)
