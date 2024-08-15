import os
import time
import pickle
import threading
from typing import Type
import screeninfo
import dearpygui.dearpygui as dpg
# import DearPyGui_DragAndDrop as dpg_dnd
# import drag_and_drop_setup
from test_creator.modules import testmode, drag_testmode
from test_creator import spawn_warning, spawn_info, classes, backupper
from cyrillic_support import CyrillicSupport, FontPreset, decode_string
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


def test_object_getter():
    return test_object


def save(modules_classes: dict[Type[classes.Round], str]):
    logger.debug('Save test function called')
    test_name = dpg.get_value('test_creator_test_name')
    test_name_decoded = decode_string(test_name)

    if test_name in os.listdir('tests'):
        logger.debug('There is another test with same name.')
        spawn_warning('Test with the same name already exists!')
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

    spawn_info(f'{test_name} was saved!')
    logger.debug(f'Test {test_name_decoded} was saved.')


def load_test():
    global test_object

    test_name = dpg.get_value('test_creator_test_name_to_open')

    if not test_name:
        return

    round_types = os.listdir(f'tests/{test_name}/')

    if not round_types:
        spawn_warning('Chosen test is empty!')
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


def open_test_maker():
    monitor = screeninfo.get_monitors()[0]
    monitor_size = (monitor.width, monitor.height)
    viewport_size = (833, 700)

    dpg.create_context()
    # dpg_dnd.initialize()
    dpg.create_viewport(
        title='Mionly v1.0: test creator', large_icon='icon.ico',
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
            dpg.add_text('Open existing test: ')
            dpg.add_combo(items=os.listdir('tests'), width=350, source='test_creator_test_name_to_open')
            dpg.add_button(label='Open', callback=lambda: load_test())

        with dpg.group(horizontal=True):
            dpg.add_text('Name of your test: ')
            dpg.add_input_text(source='test_creator_test_name', width=350, callback=lambda: sync_test_name_with_dpg())
            dpg.add_button(label='Save', callback=lambda: save(MODULES_CLASSES))

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
            pos = (
                int(dpg.get_viewport_width() / 2 - 500 / 2),
                int(dpg.get_viewport_height() / 2 - 300 / 2)
            )
            logger.debug(f'Creator crush found. Propose to load one of these backups: {list(backups_dict.values())}')

            with dpg.window(
                    label='Unexpected crush', no_resize=True, pos=pos,
                    on_close=lambda: dpg.delete_item(load_backup_window)
            ) as load_backup_window:
                dpg.add_text(
                    'It looks like the test creator was shut down unexpectedly.\n'
                    'You can use one of the saved backups:'
                )

                with dpg.group(horizontal=True):
                    dpg.add_combo(items=list(backups_dict.keys()), source='test_creator_load_backup_mtime')
                    dpg.add_button(
                        label='Load selected',
                        callback=lambda: load_backup(
                            backups_dict.get(dpg.get_value('test_creator_load_backup_mtime')),
                            load_backup_window
                        )
                    )

                dpg.add_button(label='No, thanks', callback=lambda: dpg.delete_item(load_backup_window))

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
    file = open(LOCK_FILENAME, 'w')

    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    logger.debug('Destroying context. Closing')
    dpg.destroy_context()
    logger.debug(f'Unlocking {LOCK_FILENAME}. Deleting')
    file.close()
    os.remove(LOCK_FILENAME)
