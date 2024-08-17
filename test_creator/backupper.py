import copy
import time
import pickle
import os.path
import traceback
import threading
from typing import Callable
from datetime import datetime
import dearpygui.dearpygui as dpg
from test_creator import classes, animator, messageboxes
from test_creator.language import loc
from settings import *

logger = logging.getLogger(__name__)
logging.basicConfig(format=LOGGING_FORMAT)
logger.setLevel(LOGGING_LEVEL)
previous_test_object: classes.Test | None = None
TEST_OBJECT_GETTER: Callable[[], classes.Test] | None = None
BACKUPPER_TIMEOUT_SECONDS = 60 * 2
MAX_BACKUPS_COUNT = 5


def setup(test_object_getter: Callable[[], classes.Test]):
    global TEST_OBJECT_GETTER
    TEST_OBJECT_GETTER = test_object_getter

    logger.debug(f'Auto backup timeout: {BACKUPPER_TIMEOUT_SECONDS}s. Max backups count: {MAX_BACKUPS_COUNT}')
    os.makedirs('backups', exist_ok=True)
    auto_backup_thread = threading.Thread(
        target=lambda: test_auto_backupper(check_for_unexpected_crush()),
        daemon=True
    )
    auto_backup_thread.start()


def format_exception(exception: Exception) -> str:
    formatted_exception = traceback.format_exception(type(exception), exception, exception.__traceback__)
    return ''.join(formatted_exception).rstrip('\n')


def load_backup(backup_filepath: str, load_backup_window: str | int):
    global previous_test_object

    logger.debug(f'Load backup func called. Backup path: {backup_filepath}')
    test_object = TEST_OBJECT_GETTER()

    if backup_filepath is None:
        logger.debug('Backup file is not picked')
        return

    logger.debug('Loading backup...')

    restricted_parent_children_to_remove = test_object.restricted_parent_children_to_remove
    dpg_window_for_round_previews = test_object.dpg_window_for_round_previews

    try:
        test_object = pickle.load(open(f'backups/{backup_filepath}', 'rb'))
    except Exception as e:
        logger.exception('An error occurred:', exc_info=e)
        messageboxes.spawn_warning(loc('backupper.error_when_loading_backup'))
        return

    for round_object in test_object.rounds:
        round_object.test_object_getter = TEST_OBJECT_GETTER

    previous_test_object = test_object
    test_object.restricted_parent_children_to_remove = restricted_parent_children_to_remove
    test_object.dpg_window_for_round_previews = dpg_window_for_round_previews
    test_object.regenerate_round_previews()
    animator.close_item(load_backup_window)
    logger.debug('Backup loaded')


def check_for_unexpected_crush() -> str | int | None:
    logger.debug(f'Checking for unexpected creator crush (checking for {TEST_CREATOR_LOCK_FILENAME})')

    load_backup_window = None
    if os.path.exists(TEST_CREATOR_LOCK_FILENAME):
        backups_dict = {time.ctime(os.path.getmtime(f'backups/{i}')): i for i in reversed(os.listdir('backups'))}
        size = (625, 170)
        pos = (
            int(dpg.get_viewport_width() / 2 - size[0] / 2),
            int(dpg.get_viewport_height() / 2 - size[1] / 2)
        )
        logger.debug(f'Creator crush found. Propose to load one of these backups: {list(backups_dict.values())}')

        with dpg.window(
                label=loc('creator.crush_window_label'), pos=pos, width=size[0], height=size[1],
                on_close=animator.close_item
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

            dpg.add_button(label=loc('creator.no_thanks'), callback=lambda: animator.close_item(load_backup_window))
        return load_backup_window
    return None


def test_auto_backupper(load_backup_window_tag: str | int | None):
    global previous_test_object

    while dpg.does_item_exist(load_backup_window_tag):
        # logger.debug('Load backup window exists. Waiting...')
        time.sleep(2)

    while True:
        try:
            time.sleep(BACKUPPER_TIMEOUT_SECONDS)

            new_test_object = TEST_OBJECT_GETTER()

            if not new_test_object.rounds:
                # logger.debug('There are no rounds. Skipping...')
                continue

            if new_test_object == previous_test_object:
                # logger.debug('Test was not changed. Skipping...')
                continue

            # logger.debug('Creating backup...')

            while len(os.listdir('backups')) >= MAX_BACKUPS_COUNT:
                backups = os.listdir('backups')
                backups_with_last_modified_time = {os.path.getmtime(f'backups/{k}'): k for k in backups}
                oldest_backup_time = min(backups_with_last_modified_time.keys())
                oldest_backup_filename = backups_with_last_modified_time[oldest_backup_time]
                os.remove(f'backups/{oldest_backup_filename}')

            new_backup_filepath = f'backups/backup {datetime.now().strftime("%d.%m.%Y %H-%M-%S")}.bak'
            previous_test_object = copy.deepcopy(new_test_object)
            pickle.dump(previous_test_object, open(new_backup_filepath, 'wb'))
        except Exception as e:
            logger.exception('An error occurred:', exc_info=e)
