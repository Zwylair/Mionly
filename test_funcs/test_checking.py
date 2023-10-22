import eel
import settings
import db_operations


@eel.expose
def submit_action(picked_answers: list):  # picked_answers = [ {"answer": True | False}, ... ]
    wrong_picked_answers = [i for i in picked_answers if not list(i.values())[0]]
    curr_test = db_operations.get_curr_test_json()
    max_points = settings.MAX_TEST_REWARDS[curr_test]

    db_operations.dump_progress(max_points - len(wrong_picked_answers))
