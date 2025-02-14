import dearpygui.dearpygui as dpg
from test_creator import animator, viewport_resize_handler
from shared_funcs import language, exit, messageboxes
from settings import *
import log

logger = logging.getLogger(__name__)
logging.basicConfig(level=LOGGING_LEVEL, handlers=[log.ColorHandler()] if 'PYCHARM_HOSTED' in os.environ else None)


def configure_language_changer_button():
    dpg.configure_item('shared__language_button', pos=[dpg.get_viewport_width() - 64, 7])


def open_languages_window():
    logger.debug('Opened language pick window')

    with dpg.window(label=language.loc('shared.languages'), no_resize=True, on_close=animator.close_item) as lang_window:
        with dpg.group(horizontal=True):
            dpg.add_combo(items=language.get_available_languages(), source='shared__picked_lang')
            dpg.add_button(label=language.loc('shared.apply'), callback=lambda: show_language_change_confirmation_window())
        dpg.add_text(language.loc('shared.reboot_warning'), color=(140, 140, 140))
    animator.show_item(lang_window)


def show_language_change_confirmation_window():
    new_lang = dpg.get_value('shared__picked_lang')
    if new_lang == language.chosen_language:
        return

    messageboxes.spawn_yes_no_window(
        text=language.loc('shared.exit_confirmation'),
        yes_button_callback=lambda: apply_lang(new_lang)
    )


def apply_lang(new_lang: str):
    language.set_language(new_lang)
    exit.rerun()


viewport_resize_handler.add_handler(configure_language_changer_button)
