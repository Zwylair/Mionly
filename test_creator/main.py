import os.path
import shutil
from typing import Type
import screeninfo
import dearpygui.dearpygui as dpg
import dearpygui_animate as animate
# import DearPyGui_DragAndDrop as dpg_dnd
# import drag_and_drop_setup
from test_creator import classes, messageboxes, backupper, language_picker, exit
from test_creator.cyrillic_support import CyrillicSupport, FontPreset, decode_string
from test_creator.language import loc, chosen_language
from test_creator.modules import testmode, drag_testmode
from settings import *

logger = logging.getLogger(__name__)
logging.basicConfig(format=LOGGING_FORMAT)
logger.setLevel(LOGGING_LEVEL)
test_object = classes.Test()
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


def save(modules_classes: dict[Type[classes.Round], str], exists_ok: bool = False):
    logger.debug('Save test function called')
    test_name = dpg.get_value('test_creator_test_name')
    test_name_decoded = decode_string(test_name)

    if test_name_decoded in os.listdir('tests'):
        logger.debug(f'There is another test with same name')

        if not exists_ok:
            messageboxes.spawn_yes_no_window(
                text=loc('creator.duplicate_test_name'),
                yes_button_callback=lambda: save(modules_classes, exists_ok=True)
            )
            return

        logger.debug(f'exists_ok={exists_ok}. Overwriting')
        shutil.rmtree(f'tests/{test_name_decoded}', ignore_errors=True)

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

    messageboxes.spawn_info(loc('creator.test_saved').format(test_name))
    logger.debug(f'Test {test_name_decoded} was saved.')


def load_test():
    global test_object

    test_name = dpg.get_value('test_creator_test_name_to_open')

    if not test_name:
        return

    round_types = os.listdir(f'tests/{test_name}/')

    if not round_types:
        messageboxes.spawn_warning(loc('creator.empty_test'))
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


def sync_test_name_with_dpg():
    test_object.name = dpg.get_value('test_creator_test_name')
    logger.debug(f'Test name synced with dearpygui: {test_object.name}')


def open_test_maker(main_executable: str):
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

    fonts = [
        # FontPreset(path='web/fonts/nunito/Nunito-Regular.ttf', size=28, id='nunito_titles', bind_font_as_default=False),
        FontPreset(path='web/fonts/nunito/Nunito-Regular.ttf', size=24, id='nunito', bind_font_as_default=True),
    ]
    with dpg.font_registry():
        for font in fonts:
            CyrillicSupport(font)

    with dpg.value_registry():
        dpg.add_string_value(tag='test_creator_load_backup_mtime')
        dpg.add_string_value(tag='test_creator_test_name_to_open')
        dpg.add_string_value(tag='test_creator_test_name', default_value=test_object.name)
        dpg.add_string_value(tag='test_creator_picked_lang', default_value=chosen_language)

    logger.debug('Loading textures')
    width, height, channels, data = dpg.load_image('web/images/language.png')
    with dpg.texture_registry():
        dpg.add_static_texture(width=width, height=height, default_value=data, tag='texture__language')

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
            callback=lambda: language_picker.open_languages_window(lock_file, main_executable)
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
        backupper.setup(test_object_getter)

    dpg.set_primary_window(window, True)
    # logger.debug('Setting up dearpygui drag&drop')
    # drag_and_drop_setup.setup()
    logger.debug(f'Creating and locking {TEST_CREATOR_LOCK_FILENAME}')
    lock_file = open(TEST_CREATOR_LOCK_FILENAME, 'w')

    dpg.setup_dearpygui()
    dpg.show_viewport()
    while dpg.is_dearpygui_running():
        animate.run()
        dpg.render_dearpygui_frame()
    exit.exit_mionly(lock_file)
