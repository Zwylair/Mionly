import pickle
import time
import os.path
from typing import Type
import threading
import dearpygui.dearpygui as dpg
# import DearPyGui_DragAndDrop as dpg_dnd
# import drag_and_drop_setup
import screeninfo
from test_creator import testmode, drag_testmode, classes, spawn_warning, spawn_info, test_auto_backupper, update_test_object_in_modules
from cyrillic_support import CyrillicSupport, FontPreset, decode_string

LOCK_FILENAME = '_test_creator.lock'
test_object = classes.Test.init_empty()
auto_backup_thread = threading.Thread(target=lambda: test_auto_backupper(test_object_getter), daemon=True)


def test_object_getter():
    return test_object


def save(modules_classes: dict[Type[classes.Round], str]):
    test_name = dpg.get_value('test_creator_test_name')
    test_name_decoded = decode_string(test_name)

    if test_name in os.listdir('tests'):
        spawn_warning('Test with the same name already exists!')
        return

    os.makedirs(f'tests/{test_name_decoded}', exist_ok=True)

    rounds_by_type = {}

    for test_round in test_object.rounds:
        round_type = modules_classes[test_round.__class__]

        if rounds_by_type.get(round_type) is None:
            rounds_by_type[round_type] = []
        rounds_by_type[round_type].append(test_round)

    for test_round_type, rounds in rounds_by_type.items():
        os.makedirs(f'tests/{test_name_decoded}/{test_round_type}', exist_ok=True)

        for index, test_round in enumerate(rounds):
            with open(f'tests/{test_name_decoded}/{test_round_type}/{index}.json', 'w') as file:
                file.write(test_round.dump())

    spawn_info(f'{test_name} was saved!')


def load_backup(backup_filepath: str, load_backup_window: str | int):
    global test_object

    if backup_filepath is None:
        return

    test_object = pickle.load(open(f'backups/{backup_filepath}', 'rb'))
    test_object.link_test_object_with_rounds()
    update_test_object_in_modules(test_object)
    test_object.update_round_list()
    dpg.delete_item(load_backup_window)


def open_test_maker():
    monitor = screeninfo.get_monitors()[0]
    monitor_size = (monitor.width, monitor.height)
    viewport_size = (833, 700)

    dpg.create_context()
    # dpg_dnd.initialize()
    dpg.create_viewport(
        title='Mionly: test creator', large_icon='icon.ico',
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
        dpg.add_string_value(tag='test_creator_test_name', default_value='my test')
        dpg.add_string_value(tag='test_creator_load_backup_mtime')

    with dpg.window(no_title_bar=True, no_resize=True, no_close=True, no_move=True) as window:
        test_object.dpg_window_for_round_previews = window
        modules = {
            'testmode': testmode.setup,
            'drag_testmode':  drag_testmode.setup,
        }
        modules_classes = {
            testmode.TestModeRound: 'testmode',
            drag_testmode.DragTestModeRound: 'drag_testmode',
        }

        with dpg.group(horizontal=True):
            dpg.add_text('Name of your test: ')
            dpg.add_input_text(source='test_creator_test_name', width=150)
            dpg.add_button(label='Save', callback=lambda: save(modules_classes))

        for initialiser in modules.values():
            initialiser(test_object)

        dpg.add_separator()
        test_object.restricted_parent_children_to_remove = dpg.get_item_children(window)[1]

        # check for unexpected creator crush and propose to load backup
        if os.path.exists(LOCK_FILENAME):
            backups_dict = {time.ctime(os.path.getmtime(f'backups/{i}')): i for i in reversed(os.listdir('backups'))}
            pos = (
                int(dpg.get_viewport_width() / 2 - 500 / 2),
                int(dpg.get_viewport_height() / 2 - 300 / 2)
            )

            with dpg.window(label='Unexpected crush', no_resize=True, pos=pos) as load_backup_window:
                dpg.add_text(
                    'It looks like the test creator was shut down unexpectedly.\n'
                    'You can use one of the saved backups:'
                )

                with dpg.group(horizontal=True):
                    dpg.add_combo(items=list(backups_dict.keys()), source='test_creator_load_backup_mtime')
                    dpg.add_button(
                        label='Load selected',
                        callback=lambda: load_backup(backups_dict.get(dpg.get_value('test_creator_load_backup_mtime')), load_backup_window)
                    )

                dpg.add_button(label='No, thanks', callback=lambda: dpg.delete_item(load_backup_window))

    dpg.set_primary_window(window, True)
    # drag_and_drop_setup.setup()
    auto_backup_thread.start()

    file = open(LOCK_FILENAME, 'w')
    file.close()

    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()
    os.remove(LOCK_FILENAME)
