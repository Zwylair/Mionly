import os
import random
import eel
import db
from test_funcs import test_checking


def get_random_test(available_tests: list) -> str:
    return random.choice(available_tests)


def get_all_tests() -> list:
    directory = f'tests/{"/".join(db.get_chosen_test())}'

    return_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            return_files.append('/'.join(root.split("\\")[1:]) + f'/{file}')
    return return_files


@eel.expose
def get_all_tests_count() -> int:
    return len(get_all_tests())


@eel.expose
def get_available_tests_count() -> int:
    return len(db.get_curr_available_tests())


@eel.expose
def start_testing(ww_book: str, unit: str, test: str) -> str:
    """Starts the test (dumps tests path, available and current tests) and returns the url of test webpage"""

    db.dump_chosen_test(ww_book, unit, test)

    all_tests = get_all_tests()
    curr_test = get_random_test(all_tests)
    all_tests.remove(curr_test)

    db.dump_curr_available_tests(curr_test, all_tests)
    return f'{curr_test.split("/")[0]}.html'


@eel.expose
def load_next_test() -> str:
    """Loads the next test. After dumps available and current tests,
    returns the url of next test webpage or finishes the test if there is no more available tests"""

    available_tests = db.get_curr_available_tests()

    if not available_tests:
        return end_testing()

    curr_test = get_random_test(available_tests)

    available_tests.remove(curr_test)
    db.dump_curr_available_tests(curr_test, available_tests)
    return f'{curr_test.split("/")[0]}.html'


def end_testing() -> str:
    """Ends the test. Deletes available and current tests,
        returns the url of end test webpage with congrats with test ending"""

    return '/testing_ended.html'


@eel.expose
def get_progress_results() -> dict:
    """ A shortcut to db.get_progress_result() """

    return db.get_progress_result()


@eel.expose
def get_completed_tests_count() -> int:
    """ A shortcut to db.get_completed_tests_count() """

    return db.get_completed_tests_count()
