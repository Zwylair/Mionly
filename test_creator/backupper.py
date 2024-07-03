import copy
import time
import pickle
import os.path
import traceback
from datetime import datetime
from typing import Callable
from test_creator.classes import Test

BACKUPPER_TIMEOUT_SECONDS = 5
MAX_BACKUPS_COUNT = 5


def format_exception(exception: Exception) -> str:
    formatted_exception = traceback.format_exception(type(exception), exception, exception.__traceback__)
    return ''.join(formatted_exception).rstrip('\n')


def test_auto_backupper(test_object_getter: Callable[[], Test]):
    previous_test_object = None

    while True:
        try:
            time.sleep(BACKUPPER_TIMEOUT_SECONDS)

            new_test_object = test_object_getter()
            compare_test_object = copy.deepcopy(new_test_object)
            compare_test_object.remove_test_object_link_from_rounds()

            if not new_test_object.rounds:
                continue

            if compare_test_object == previous_test_object:
                continue

            os.makedirs('backups', exist_ok=True)

            while len(os.listdir('backups')) >= MAX_BACKUPS_COUNT:
                backups = os.listdir('backups')
                backups_with_last_modified_time = {os.path.getmtime(f'backups/{k}'): k for k in backups}
                oldest_backup_time = min(backups_with_last_modified_time.keys())
                oldest_backup_filename = backups_with_last_modified_time[oldest_backup_time]
                os.remove(f'backups/{oldest_backup_filename}')

            previous_test_object = copy.deepcopy(new_test_object)
            previous_test_object.remove_test_object_link_from_rounds()
            new_backup_filepath = f'backups/backup {datetime.now().strftime("%d.%m.%Y %H-%M-%S")}.bak'
            pickle.dump(previous_test_object, open(new_backup_filepath, 'wb'))
        except Exception as e:
            print(format_exception(e))
