import sys
import subprocess
from typing import TextIO
import dearpygui.dearpygui as dpg
from test_creator import animator, exit, language
from settings import *

logger = logging.getLogger(__name__)
logging.basicConfig(format=LOGGING_FORMAT)
logger.setLevel(LOGGING_LEVEL)


def open_languages_window(lock_file: TextIO, main_executable: str):
    logger.debug('Opened language pick window')

    with dpg.window(label=language.loc('creator.languages'), no_resize=True, on_close=animator.close_item) as lang_window:
        with dpg.group(horizontal=True):
            dpg.add_combo(items=language.get_available_languages(), source='test_creator_picked_lang')
            dpg.add_button(label=language.loc('creator.apply'), callback=lambda: set_lang(lock_file, main_executable))
        dpg.add_text(language.loc('creator.reboot_warning'), color=(140, 140, 140))
    animator.show_item(lang_window)


def set_lang(lock_file: TextIO, main_executable: str):
    new_lang = dpg.get_value('test_creator_picked_lang')
    if new_lang == language.chosen_language:
        return

    with dpg.window(on_close=animator.close_item) as pick_language_confirmation:
        dpg.add_text(language.loc('creator.exit_confirmation'))

        with dpg.group(horizontal=True):
            yes_button = dpg.add_button(
                label=language.loc('creator.exit_confirmation_yes_button'),
                callback=lambda: apply_lang(new_lang, lock_file, main_executable)
            )
            dpg.add_button(
                label=language.loc('creator.cancel'),
                callback=lambda: animator.close_item(pick_language_confirmation)
            )
        dpg.bind_item_theme(yes_button, 'red_button_theme')
    animator.show_item(pick_language_confirmation)


def apply_lang(new_lang: str, lock_file: TextIO, main_executable: str):
    language.set_language(new_lang)

    if getattr(sys, 'frozen', True):
        logger.debug('Mionly is not frozen. Restart via launching script')
        logger.debug(f'Restart command: "{sys.executable}" "{main_executable}"')
        subprocess.Popen(f'"{sys.executable}" "{main_executable}"')
    else:
        logger.debug('Mionly is frozen. Restart via launching exe file')
        logger.debug(f'Restart command: "{sys.executable}"')
        subprocess.Popen(f'{sys.executable}')
    exit.exit_mionly(lock_file)
