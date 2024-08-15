import copy
import time
import pickle
import os.path
import traceback
from typing import Callable
from datetime import datetime
import dearpygui.dearpygui as dpg
from test_creator.classes import Test

previous_test_object: Test | None = None
BACKUPPER_TIMEOUT_SECONDS = 5
MAX_BACKUPS_COUNT = 5


def format_exception(exception: Exception) -> str:
    formatted_exception = traceback.format_exception(type(exception), exception, exception.__traceback__)
    return ''.join(formatted_exception).rstrip('\n')


def setup():
    os.makedirs('backups', exist_ok=True)


def test_auto_backupper(test_object_getter: Callable[[], Test], load_backup_window_tag: str | int | None):
    global previous_test_object

    while dpg.does_item_exist(load_backup_window_tag):
        time.sleep(2)

    while True:
        try:
            time.sleep(BACKUPPER_TIMEOUT_SECONDS)

            new_test_object = test_object_getter()

            if not new_test_object.rounds:
                continue

            if new_test_object == previous_test_object:
                continue

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
            print(format_exception(e))
