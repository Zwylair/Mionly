import dearpygui.dearpygui as dpg
from test_creator.language import loc
from test_creator import animator
from settings import *

logger = logging.getLogger(__name__)
logging.basicConfig(format=LOGGING_FORMAT)
logger.setLevel(LOGGING_LEVEL)


def spawn_warning(text: str):
    logger.debug(f'Spawning warning with text: {text}')

    with dpg.window(label=loc('messageboxes.warning')) as window:
        dpg.add_text(default_value=text, color=(255, 190, 190))
        dpg.render_dearpygui_frame()
        dpg.set_item_pos(
            window,
            pos=[
                int(dpg.get_viewport_width() / 2 - dpg.get_item_width(window) / 2),
                int(dpg.get_viewport_height() / 2 - dpg.get_item_height(window) / 2)
            ]
        )
    animator.show_item(window)


def spawn_info(text: str):
    logger.debug(f'Spawning info with text: {text}')

    with dpg.window(label=loc('messageboxes.info')) as window:
        dpg.add_text(default_value=text, color=(190, 230, 255))
        dpg.render_dearpygui_frame()
        dpg.set_item_pos(
            window,
            pos=[
                int(dpg.get_viewport_width() / 2 - dpg.get_item_width(window) / 2),
                int(dpg.get_viewport_height() / 2 - dpg.get_item_height(window) / 2)
            ]
        )
    animator.show_item(window)
