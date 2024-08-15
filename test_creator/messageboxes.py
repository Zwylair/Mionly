import dearpygui.dearpygui as dpg
from settings import *

logger = logging.getLogger(__name__)
logging.basicConfig(format=LOGGING_FORMAT)
logger.setLevel(LOGGING_LEVEL)


def spawn_warning(text: str):
    logger.debug(f'Spawning warning with text: {text}')

    width, height = [300, 70]

    pos = (
        int(dpg.get_viewport_width() / 2 - width / 2),
        int(dpg.get_viewport_height() / 2 - height / 2)
    )

    with dpg.window(label='Warning', no_resize=True, pos=pos):
        dpg.add_text(default_value=text, color=(255, 190, 190))


def spawn_info(text: str):
    logger.debug(f'Spawning info with text: {text}')

    width, height = [300, 70]

    pos = (
        int(dpg.get_viewport_width() / 2 - width / 2),
        int(dpg.get_viewport_height() / 2 - height / 2)
    )

    with dpg.window(label='Info', no_resize=True, pos=pos):
        dpg.add_text(default_value=text, color=(190, 230, 255))
