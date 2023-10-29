import eel
import db
from loader import lessons_list


@eel.expose
def get_test_data() -> str:
    ww_book, unit, test = db.get_chosen_test()
    curr_test = db.get_curr_test_json()

    with open(f'tests/{ww_book}/{unit}/{test}/{curr_test}') as file:
        return file.read()
