import os
from typing import TextIO
import dearpygui.dearpygui as dpg
from settings import *

logger = logging.getLogger(__name__)
logging.basicConfig(format=LOGGING_FORMAT)
logger.setLevel(LOGGING_LEVEL)


def exit_mionly(lock_file: TextIO):
    logger.debug(f'Unlocking {TEST_CREATOR_LOCK_FILENAME}. Deleting')
    lock_file.close()
    os.remove(TEST_CREATOR_LOCK_FILENAME)
    logger.debug('Destroying context. Closing')
    dpg.destroy_context()
