from typing import Callable, Any
import dearpygui.dearpygui as dpg
from test_creator.language import loc
from test_creator import animator
from settings import *

logger = logging.getLogger(__name__)
logging.basicConfig(format=LOGGING_FORMAT)
logger.setLevel(LOGGING_LEVEL)


def spawn_warning(text: str):
    logger.debug(f'Spawning warning with text: {text}')

    with dpg.window(label=loc('messageboxes.warning'), on_close=animator.close_item) as window:
        dpg.add_text(default_value=text, color=(255, 190, 190))
    animator.show_item(window)


def spawn_info(text: str):
    logger.debug(f'Spawning info with text: {text}')

    with dpg.window(label=loc('messageboxes.info'), on_close=animator.close_item) as window:
        dpg.add_text(default_value=text, color=(190, 230, 255))
    animator.show_item(window)


def spawn_yes_no_window(
        text: str,
        yes_button_callback: Callable,
        yes_button_text: str = loc('messagebox.yes'),
        no_button_text: str = loc('messagebox.no'),
        no_button_callback: Callable[[], Any] | None = None
):
    with dpg.window(on_close=animator.close_item) as window:
        if no_button_callback is None:
            def no_button_callback():
                animator.close_item(window)

        dpg.add_text(text)

        with dpg.group(horizontal=True):
            yes_button = dpg.add_button(label=yes_button_text, callback=yes_button_callback)
            dpg.add_button(label=no_button_text, callback=no_button_callback)
        dpg.bind_item_theme(yes_button, 'red_button_theme')
    animator.show_item(window)
