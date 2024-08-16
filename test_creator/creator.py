import sys
import time
import pickle
import os.path
import threading
import subprocess
from typing import Type, TextIO
import screeninfo
import dearpygui.dearpygui as dpg
# import DearPyGui_DragAndDrop as dpg_dnd
# import drag_and_drop_setup
from test_creator.modules import testmode, drag_testmode
from test_creator import spawn_warning, spawn_info, classes, backupper
from cyrillic_support import CyrillicSupport, FontPreset, decode_string
from test_creator.language import loc
from test_creator import language
from settings import *

logger = logging.getLogger(__name__)
logging.basicConfig(format=LOGGING_FORMAT)
logger.setLevel(LOGGING_LEVEL)
test_object = classes.Test()
LOCK_FILENAME = 'test_creator.lock'
MODULES = {
    'testmode': testmode.setup,
    'drag_testmode': drag_testmode.setup,
}
MODULES_CLASSES = {
    testmode.TestModeRound: 'testmode',
    drag_testmode.DragTestModeRound: 'drag_testmode',
}


def exit_mionly(lock_file: TextIO):
    logger.debug(f'Unlocking {LOCK_FILENAME}. Deleting')
    lock_file.close()
    os.remove(LOCK_FILENAME)
    logger.debug('Destroying context. Closing')
    dpg.destroy_context()


def test_object_getter():
    return test_object


def save(modules_classes: dict[Type[classes.Round], str]):
    logger.debug('Save test function called')
    test_name = dpg.get_value('test_creator_test_name')
    test_name_decoded = decode_string(test_name)

    if test_name in os.listdir('tests'):
        logger.debug('There is another test with same name.')
        spawn_warning(loc('creator.test_already_exists'))
        return

    os.makedirs(f'tests/{test_name_decoded}', exist_ok=True)
    logger.debug('Filtering rounds by its type...')

    rounds_by_type = {}
    for test_round in test_object.rounds:
        round_type = modules_classes[test_round.__class__]

        if rounds_by_type.get(round_type) is None:
            rounds_by_type[round_type] = []
        rounds_by_type[round_type].append(test_round)

    logger.debug('Creating round types folders and dumping them...')
    for test_round_type, rounds in rounds_by_type.items():
        os.makedirs(f'tests/{test_name_decoded}/{test_round_type}', exist_ok=True)

        for index, test_round in enumerate(rounds):
            with open(f'tests/{test_name_decoded}/{test_round_type}/{index}.json', 'w') as file:
                file.write(test_round.dumps())

    spawn_info(loc('creator.test_saved').format(test_name))
    logger.debug(f'Test {test_name_decoded} was saved.')


def load_test():
    global test_object

    test_name = dpg.get_value('test_creator_test_name_to_open')

    if not test_name:
        return

    round_types = os.listdir(f'tests/{test_name}/')

    if not round_types:
        spawn_warning(loc('creator.empty_test'))
        return

    logger.debug(f'Opening test "{test_name}"')
    dpg.set_value('test_creator_test_name', test_name)
    sync_test_name_with_dpg()
    reversed_modules_classes = {v: k for k, v in MODULES_CLASSES.items()}

    for round_type in round_types:
        for round_name in os.listdir(f'tests/{test_name}/{round_type}/'):
            if round_type not in reversed_modules_classes:
                logger.info(f'Unknown round mode: {round_type} ("{test_name}" test)')
                break

            with open(f'tests/{test_name}/{round_type}/{round_name}', 'r') as file:
                test_object.add_round(reversed_modules_classes[round_type].loads(file.read(), test_object_getter))
    test_object.regenerate_round_previews()


def load_backup(backup_filepath: str, load_backup_window: str | int):
    logger.debug(f'Load backup func called. Backup path: {backup_filepath}')
    global test_object

    if backup_filepath is None:
        logger.debug('Backup file is not picked.')
        return

    logger.debug('Loading backup...')

    restricted_parent_children_to_remove = test_object.restricted_parent_children_to_remove
    dpg_window_for_round_previews = test_object.dpg_window_for_round_previews
    test_object = pickle.load(open(f'backups/{backup_filepath}', 'rb'))

    for round_object in test_object.rounds:
        round_object.test_object_getter = test_object_getter

    backupper.previous_test_object = test_object
    test_object.restricted_parent_children_to_remove = restricted_parent_children_to_remove
    test_object.dpg_window_for_round_previews = dpg_window_for_round_previews
    test_object.regenerate_round_previews()
    dpg.delete_item(load_backup_window)
    logger.debug('Backup loaded.')


def sync_test_name_with_dpg():
    test_object.name = dpg.get_value('test_creator_test_name')
    logger.debug(f'Test name synced with dearpygui: {test_object.name}')


def open_languages_window(lock_file: TextIO):
    logger.debug('Opened language pick window')

    def set_lang():
        def apply_lang():
            language.set_language(new_lang)

            if getattr(sys, 'frozen', False):
                logger.debug(f'Restart command: {sys.executable}')
                subprocess.Popen(sys.executable)
            else:
                py_path = os.path.join(os.path.dirname(TEST_MAKER_ROOT_FILE), 'venv/scripts/python.exe').replace('/', '\\')
                logger.debug(f'Restart command: "{py_path}" "{TEST_MAKER_ROOT_FILE}"')
                subprocess.Popen(f'"{py_path}" "{TEST_MAKER_ROOT_FILE}"')
            exit_mionly(lock_file)

        new_lang = dpg.get_value('test_creator_picked_lang')
        if new_lang == language.chosen_language:
            return

        with dpg.window() as pick_language_confirmation:
            dpg.add_text(loc('creator.exit_confirmation'))

            with dpg.group(horizontal=True):
                yes_button = dpg.add_button(label=loc('creator.exit_confirmation_yes_button'), callback=lambda: apply_lang())
                dpg.add_button(label=loc('creator.cancel'), callback=lambda: dpg.delete_item(pick_language_confirmation))
            dpg.bind_item_theme(yes_button, 'red_button_theme')
            dpg.render_dearpygui_frame()
            dpg.set_item_pos(
                pick_language_confirmation,
                pos=[
                    int(dpg.get_viewport_width() / 2 - dpg.get_item_width(pick_language_confirmation) / 2),
                    int(dpg.get_viewport_height() / 2 - dpg.get_item_height(pick_language_confirmation) / 2)
                ]
            )

    with dpg.window(label=loc('creator.languages'), no_resize=True) as lang_window:
        with dpg.group(horizontal=True):
            dpg.add_combo(items=language.get_available_languages(), source='test_creator_picked_lang')
            dpg.add_button(label=loc('creator.apply'), callback=lambda: set_lang())
        dpg.add_text(loc('creator.reboot_warning'), color=(140, 140, 140))
        dpg.render_dearpygui_frame()
        dpg.set_item_pos(
            lang_window,
            pos=[
                int(dpg.get_viewport_width() / 2 - dpg.get_item_width(lang_window) / 2),
                int(dpg.get_viewport_height() / 2 - dpg.get_item_height(lang_window) / 2)
            ]
        )


def open_test_maker():
    monitor = screeninfo.get_monitors()[0]
    monitor_size = (monitor.width, monitor.height)
    viewport_size = (833, 700)

    dpg.create_context()
    # dpg_dnd.initialize()
    dpg.create_viewport(
        title="Mionly v2.0: test creator", large_icon='icon.ico',
        width=viewport_size[0], height=viewport_size[1],
        x_pos=int(monitor_size[0] / 2 - viewport_size[0] / 2),
        y_pos=int(monitor_size[1] / 2 - viewport_size[1] / 2)
    )

    logger.debug('Initializing fonts')
    fonts = [
        # FontPreset(path='web/fonts/nunito/Nunito-Regular.ttf', size=28, id='nunito_titles', bind_font_as_default=False),
        FontPreset(path='web/fonts/nunito/Nunito-Regular.ttf', size=24, id='nunito', bind_font_as_default=True),
    ]
    with dpg.font_registry():
        for font in fonts:
            CyrillicSupport(font)

    logger.debug('Creating registry')
    with dpg.value_registry():
        dpg.add_string_value(tag='test_creator_load_backup_mtime')
        dpg.add_string_value(tag='test_creator_test_name_to_open')
        dpg.add_string_value(tag='test_creator_test_name', default_value=test_object.name)
        dpg.add_string_value(tag='test_creator_picked_lang', default_value=language.chosen_language)

    logger.debug('Loading textures')

    width, height, channels, data = dpg.load_image('web/images/language.png')
    with dpg.texture_registry():
        dpg.add_static_texture(width=width, height=height, default_value=data, tag='texture__language')

    logger.debug('Setting up themes')
    with dpg.theme() as global_theme:
        with dpg.theme_component(dpg.mvButton, enabled_state=False):
            dpg.add_theme_color(dpg.mvThemeCol_Button, (48, 48, 50), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (48, 48, 50), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (48, 48, 50), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_Text, (168, 168, 168), category=dpg.mvThemeCat_Core)

    with dpg.theme(tag='red_button_theme'):
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Button, (87, 47, 63), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (118, 44, 34), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (78, 38, 38), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 255, 255), category=dpg.mvThemeCat_Core)

    with dpg.theme(tag='green_button_theme'):
        with dpg.theme_component(dpg.mvButton):
            dpg.add_theme_color(dpg.mvThemeCol_Button, (51, 77, 55), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (44, 118, 34), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (34, 88, 24), category=dpg.mvThemeCat_Core)
            dpg.add_theme_color(dpg.mvThemeCol_Text, (255, 255, 255), category=dpg.mvThemeCat_Core)

    dpg.bind_theme(global_theme)

    with dpg.window(no_title_bar=True, no_resize=True, no_close=True, no_move=True) as window:
        test_object.dpg_window_for_round_previews = window

        with dpg.group(horizontal=True):
            dpg.add_text(loc('creator.open_test'))
            dpg.add_combo(items=os.listdir('tests'), width=350, source='test_creator_test_name_to_open')
            dpg.add_button(label=loc('creator.open'), callback=lambda: load_test())

        dpg.add_image_button(
            texture_tag='texture__language', width=32, height=32, pos=[dpg.get_viewport_width() - 64, 7],
            callback=lambda: open_languages_window(lock_file)
        )

        with dpg.group(horizontal=True):
            dpg.add_text(loc('creator.test_name_label'))
            dpg.add_input_text(source='test_creator_test_name', width=350, callback=lambda: sync_test_name_with_dpg())
            dpg.add_button(label=loc('creator.save'), callback=lambda: save(MODULES_CLASSES))

        dpg.add_separator()

        logger.debug('Initializing modules')
        for initialiser in MODULES.values():
            initialiser(test_object_getter)

        dpg.add_separator()
        test_object.restricted_parent_children_to_remove = dpg.get_item_children(window)[1]

        # check for unexpected creator crush and propose to load backup
        logger.debug(f'Checking for unexpected creator crush (checking for {LOCK_FILENAME})')

        load_backup_window = None
        if os.path.exists(LOCK_FILENAME):
            backups_dict = {time.ctime(os.path.getmtime(f'backups/{i}')): i for i in reversed(os.listdir('backups'))}
            size = (625, 170)
            pos = (
                int(dpg.get_viewport_width() / 2 - size[0] / 2),
                int(dpg.get_viewport_height() / 2 - size[1] / 2)
            )
            logger.debug(f'Creator crush found. Propose to load one of these backups: {list(backups_dict.values())}')

            with dpg.window(
                    label=loc('creator.crush_window_label'), pos=pos, width=size[0], height=size[1],
                    on_close=lambda: dpg.delete_item(load_backup_window)
            ) as load_backup_window:
                dpg.add_text(loc('creator.crush_window_text'))

                with dpg.group(horizontal=True):
                    dpg.add_combo(items=list(backups_dict.keys()), source='test_creator_load_backup_mtime')
                    dpg.add_button(
                        label=loc('creator.load_selected'),
                        callback=lambda: load_backup(
                            backups_dict.get(dpg.get_value('test_creator_load_backup_mtime')),
                            load_backup_window
                        )
                    )

                dpg.add_button(label=loc('creator.no_thanks'), callback=lambda: dpg.delete_item(load_backup_window))

    dpg.set_primary_window(window, True)
    # logger.debug('Setting up dearpygui drag&drop')
    # drag_and_drop_setup.setup()
    logger.debug('Setting up backupper and starting thread')
    backupper.setup()
    auto_backup_thread = threading.Thread(
        target=lambda: backupper.test_auto_backupper(test_object_getter, load_backup_window),
        daemon=True
    )
    auto_backup_thread.start()

    logger.debug(f'Creating and locking lockfile ({LOCK_FILENAME})')
    lock_file = open(LOCK_FILENAME, 'w')

    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    exit_mionly(lock_file)
