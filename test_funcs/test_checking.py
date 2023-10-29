import base64
import json
import eel
import settings
import loader
import rot1
import db


@eel.expose
def submit_action(picked_answers: list):
    curr_test = db.get_curr_test_json()
    max_points = settings.MAX_TEST_REWARDS[curr_test]

    if curr_test == 'testmode.json':  # picked_answers = [ {"answer": True | False}, ... ]
        wrong_picked_answers = [i for i in picked_answers if not list(i.values())[0]]
        db.dump_progress(max_points - len(wrong_picked_answers))  # is designed for a mode where you can put a lot of words

    elif curr_test == 'drag_testmode.json':  # picked_answers = [ {"answer": [True | False, position]}, ... ]
        test_data = loader.get_test_data()
        test_data = rot1.rot1_decrypt(test_data)
        test_data = base64.b64decode(test_data.encode()).decode()
        test_data = json.loads(test_data)

        # sifting out wrong answers (wrong answers always have position 0)
        all_right_answers = [item for item in test_data['answers'] if item[list(item.keys())[0]][1] != 0]

        # sorting by position
        all_right_answers.sort(key=lambda x: x[list(x.keys())[0]][1])

        wrong_picked_answers = 0
        for picked_answer, right_answer in zip(picked_answers, all_right_answers):
            if picked_answer != right_answer:
                wrong_picked_answers += 1

        db.dump_progress(max_points - wrong_picked_answers)
