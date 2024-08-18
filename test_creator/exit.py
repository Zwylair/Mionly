import os
import typing
import dearpygui.dearpygui as dpg
from settings import *

logger = logging.getLogger(__name__)
logging.basicConfig(format=LOGGING_FORMAT)
logger.setLevel(LOGGING_LEVEL)
lockfile: typing.TextIO | None = None


def exit_mionly():
    logger.debug(f'Unlocking {TEST_CREATOR_LOCK_FILENAME}')
    lockfile.close()
    os.remove(TEST_CREATOR_LOCK_FILENAME)

    logger.debug('Stopping DearPyGui')
    dpg.stop_dearpygui()
