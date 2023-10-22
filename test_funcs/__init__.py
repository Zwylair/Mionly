import os
import random
import eel
import db_operations
import settings
from test_funcs import test_checking


def get_random_test(available_tests: list) -> str:
    return random.choice(available_tests)


@eel.expose
def get_all_tests_count() -> int:
    return len(os.listdir(f'tests/{"/".join(db_operations.get_chosen_test())}'))


@eel.expose
def get_available_tests_count() -> int:
    return len(db_operations.get_curr_available_tests())


@eel.expose
def start_testing(ww_book: str, unit: str, test: str) -> str:
    """Starts the test (dump tests path, available and current tests) and returns the url of current test webpage"""

    db_operations.dump_chosen_test(ww_book, unit, test)

    available_tests = os.listdir(f'tests/{ww_book}/{unit}/{test}')
    curr_test = get_random_test(available_tests)
    available_tests.remove(curr_test)

    db_operations.dump_curr_available_tests(curr_test, available_tests)
    return settings.TEST_JSON_TO_WEBPAGE[curr_test]


@eel.expose
def load_next_test() -> str:
    """Loads the next test. After that dumps available and current tests,
    returns the url of next test webpage or finishes the test if there is no more available tests"""

    available_tests = db_operations.get_curr_available_tests()

    if available_tests == ['']:
        return end_testing()

    curr_test = get_random_test(available_tests)

    available_tests.remove(curr_test)
    db_operations.dump_curr_available_tests(curr_test, available_tests)
    return settings.TEST_JSON_TO_WEBPAGE[curr_test]


def end_testing() -> str:
    """Ends the test. Deletes available and current tests,
        returns the url of end test webpage with congrats with test ending"""

    # here the code that doing various maths
    progress = db_operations.get_progress()
    given_points = sum([i for i in progress.values()])
    max_points = sum([settings.MAX_TEST_REWARDS[i] for i in progress.keys()])

    wrong = max_points - given_points
    right = max_points - wrong

    db_operations.dump_progress_results(wrong, right)

    return '/testing_ended.html'


@eel.expose
def get_progress_results() -> dict:
    """ A shortcut to db.get_progress_result() """

    return db_operations.get_progress_result()
