import sys
import json
import os.path
import pathlib
import zipfile
import threading
from typing import Any
import screeninfo
import filedialpy
import dearpygui.dearpygui as dpg
import dearpygui_animate as animate
# import DearPyGui_DragAndDrop as dpg_dnd
# import drag_and_drop_setup
from test_creator import classes, messageboxes, backupper, language_picker, exit, animator, viewport_resize_handler
from test_creator.cyrillic_support import CyrillicSupport, FontPreset, decode_string
from test_creator.language import loc, chosen_language
from test_creator.modules import testmode, drag_testmode
from settings import *
import log

if sys.stdout is not None:
    import faulthandler
    faulthandler.enable()

logger = logging.getLogger(__name__)
logging.basicConfig(level=LOGGING_LEVEL, handlers=log.get_handler_for_me())
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


def test_object_setter(local_test_object: classes.Test):
    global test_object
    test_object = local_test_object


def save(exists_ok: bool = False, confirm_window_tag: str | int = None):
    logger.debug('Save test function called')
    test_name = dpg.get_value('test_creator_test_name')
    test_name_decoded = decode_string(test_name)
    output_test_file_path = os.path.join('tests', f'{test_name_decoded}.mionly')

    if os.path.exists(output_test_file_path):
        logger.debug(f'There is another test with same name')

        if not exists_ok:
            messageboxes.spawn_yes_no_window(
                text=loc('creator.duplicate_test_name'),
                yes_button_callback=lambda window_tag: save(exists_ok=True, confirm_window_tag=window_tag)
            )
            return

        logger.debug(f'exists_ok={exists_ok}. Overwriting')
        os.remove(output_test_file_path)
        if dpg.does_item_exist(confirm_window_tag):
            animator.close_item(confirm_window_tag)

    output_test_file = zipfile.ZipFile(output_test_file_path, mode='w', compression=zipfile.ZIP_DEFLATED)

    round_count_by_type = {}
    for test_round in test_object.rounds:
        test_round: Any  # actually will always be a subclass of Round
        round_type = MODULES_CLASSES.get(test_round.__class__)
        round_count_by_type[round_type] = round_count_by_type.get(round_type, -1) + 1

        output_test_file.writestr(
            zipfile.ZipInfo(f'{round_type}/{round_count_by_type[round_type]}.json'),
            test_round.dumps()
        )

    output_test_file.writestr(
        zipfile.ZipInfo('test_creator_info.json'),
        json.dumps(
            {
                'round_types': list(round_count_by_type.keys())
            }
        )
    )

    messageboxes.spawn_info(loc('creator.test_saved').format(test_name))
    logger.debug(f'Test {test_name_decoded} was saved')
    output_test_file.close()


def load_test(from_file: str = None):
    global test_object

    test_name = pathlib.Path(from_file).stem if from_file else dpg.get_value('test_creator_test_name_to_open')

    if not test_name:
        return

    logger.debug(f'Opening test "{test_name}"')

    dpg.set_value('test_creator_test_name', test_name)
    reversed_modules_classes = {v: k for k, v in MODULES_CLASSES.items()}
    has_loading_round_error = False

    test_file_path = from_file if from_file else os.path.join('tests', f'{test_name}.mionly')
    test_file = zipfile.ZipFile(test_file_path, 'r')
    test_info = json.loads(test_file.read('test_creator_info.json'))
    round_types = test_info.get('round_types', [])

    if not round_types:
        messageboxes.spawn_warning(loc('creator.empty_test'))
        return

    for file in test_file.filelist:
        if file.is_dir():
            continue

        round_type = os.path.dirname(file.filename).split('/')[0]

        if round_type not in round_types:  # other dir like 'media' etc.
            continue

        try:
            test_object.rounds.append(
                reversed_modules_classes[round_type].loads(
                    test_file.read(file).decode(),
                    test_object_getter
                )
            )
        except json.JSONDecodeError:
            has_loading_round_error = True

    if has_loading_round_error:
        messageboxes.spawn_warning(loc('creator.error_when_loading_test'))
    test_file.close()
    sync_test_name_with_dpg()
    test_object.regenerate_round_previews()


def sync_test_name_with_dpg():
    test_object.name = dpg.get_value('test_creator_test_name')
    logger.debug(f'Test name synced with dearpygui: {test_object.name}')


def open_test_maker(main_executable: str):
    monitor = screeninfo.get_monitors()[0]
    monitor_size = (monitor.width, monitor.height)
    viewport_size = (1000, 700)

    dpg.create_context()
    # dpg_dnd.initialize()
    dpg.create_viewport(
        title='Mionly v2.0: test creator', large_icon=os.path.join(TEST_CREATOR_DATA_PATH, 'images/icon.ico'),
        width=viewport_size[0], height=viewport_size[1],
        x_pos=int(monitor_size[0] / 2 - viewport_size[0] / 2),
        y_pos=int(monitor_size[1] / 2 - viewport_size[1] / 2)
    )

    with dpg.font_registry():
        CyrillicSupport(
            FontPreset(
                path=os.path.join(TEST_CREATOR_DATA_PATH, 'fonts/nunito/Nunito-Regular.ttf'),
                size=24, id='nunito', bind_font_as_default=True
            )
        )

    with dpg.value_registry():
        dpg.add_string_value(tag='test_creator_load_backup_mtime')
        dpg.add_string_value(tag='test_creator_test_name_to_open')
        dpg.add_string_value(tag='test_creator_test_name', default_value=test_object.name)
        dpg.add_string_value(tag='test_creator_picked_lang', default_value=chosen_language)

    logger.debug('Loading textures')
    width, height, channels, data = dpg.load_image(os.path.join(TEST_CREATOR_DATA_PATH, 'images/language.png'))
    with dpg.texture_registry():
        dpg.add_static_texture(width=width, height=height, default_value=data, tag='texture__language')

    with dpg.theme() as global_theme:
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_style(dpg.mvStyleVar_WindowTitleAlign, 0.5, 0.5, category=dpg.mvThemeCat_Core)
            dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 7, category=dpg.mvThemeCat_Core)

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
        available_tests_to_open = [pathlib.Path(i).stem for i in os.listdir('tests') if i.endswith('.mionly')]

        # open test items
        with dpg.group(horizontal=True, horizontal_spacing=15):
            with dpg.group(horizontal=True):
                dpg.add_text(loc('creator.open_test'))
                dpg.add_combo(items=available_tests_to_open, width=350, source='test_creator_test_name_to_open')
                dpg.add_button(label=loc('creator.open'), callback=lambda: load_test())

            dpg.add_text(loc('creator.or'))

            dpg.add_button(
                label=loc('creator.browse'),
                callback=lambda: load_test(
                    from_file=filedialpy.openFile(
                        title='Select Mionly test file',
                        filter=['*.mionly']
                    )
                )
            )

        dpg.add_image_button(
            texture_tag='texture__language', width=32, height=32, pos=[dpg.get_viewport_width() - 64, 7],
            tag='test_creator__language_button',
            callback=lambda: language_picker.open_languages_window()
        )

        with dpg.group(horizontal=True):
            dpg.add_text(loc('creator.test_name_label'))
            dpg.add_input_text(source='test_creator_test_name', width=350, callback=lambda: sync_test_name_with_dpg())
            dpg.add_button(label=loc('creator.save'), callback=lambda: save())

        dpg.add_separator()

        logger.debug('Initializing modules')

        with dpg.group(horizontal=True):
            for initializer in MODULES.values():
                initializer(test_object_getter)

        dpg.add_separator()
    test_object.restricted_parent_children_to_remove = dpg.get_item_children(window)[1]

    dpg.set_primary_window(window, True)
    # logger.debug('Setting up dearpygui drag&drop')
    # drag_and_drop_setup.setup()
    dpg.setup_dearpygui()
    dpg.show_viewport()

    backupper.setup(test_object_getter, test_object_setter)
    viewport_resize_handler.setup()
    setup_exit_thread = threading.Thread(target=lambda: exit.setup(main_executable), daemon=True)
    setup_exit_thread.start()

    while dpg.is_dearpygui_running():
        animate.run()
        dpg.render_dearpygui_frame()
    exit.stop_mionly()
