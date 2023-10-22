import json

import eel
import db_operations
from loader import lessons_list


@eel.expose
def get_test_data() -> dict:
    ww_book, unit, test = db_operations.get_chosen_test()
    curr_test = db_operations.get_curr_test_json()

    with open(f'tests/{ww_book}/{unit}/{test}/{curr_test}') as file:
        return json.loads(file.read())
