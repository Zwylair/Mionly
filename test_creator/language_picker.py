import sys
import subprocess
import dearpygui.dearpygui as dpg
from test_creator import animator, exit, language, messageboxes, viewport_resize_handler
from settings import *
import log

logger = logging.getLogger(__name__)
logging.basicConfig(level=LOGGING_LEVEL, handlers=[log.ColorHandler()])


def configure_language_changer_button():
    dpg.configure_item('test_creator__language_button', pos=[dpg.get_viewport_width() - 64, 7])


def open_languages_window(main_executable: str):
    logger.debug('Opened language pick window')

    with dpg.window(label=language.loc('creator.languages'), no_resize=True, on_close=animator.close_item) as lang_window:
        with dpg.group(horizontal=True):
            dpg.add_combo(items=language.get_available_languages(), source='test_creator_picked_lang')
            dpg.add_button(label=language.loc('creator.apply'), callback=lambda: set_lang(main_executable))
        dpg.add_text(language.loc('creator.reboot_warning'), color=(140, 140, 140))
    animator.show_item(lang_window)


def set_lang(main_executable: str):
    new_lang = dpg.get_value('test_creator_picked_lang')
    if new_lang == language.chosen_language:
        return

    messageboxes.spawn_yes_no_window(
        text=language.loc('creator.exit_confirmation'),
        yes_button_callback=lambda: apply_lang(new_lang, main_executable)
    )


def apply_lang(new_lang: str, main_executable: str):
    language.set_language(new_lang)
    exit.stop_mionly()

    if getattr(sys, 'frozen', True):
        logger.debug('Mionly is not frozen. Restart via launching script')
        logger.debug(f'Restart command: "{sys.executable}" "{main_executable}"')
        subprocess.Popen(
            [sys.executable, main_executable],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    else:
        logger.debug('Mionly is frozen. Restart via launching exe file')
        logger.debug(f'Restart command: "{sys.executable}"')
        subprocess.Popen(
            [sys.executable],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    exit.exit_app()


viewport_resize_handler.add_handler(configure_language_changer_button)
