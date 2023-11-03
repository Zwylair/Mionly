import base64
import json
import eel
import loader
import rot1
import db


def get_test_data() -> dict:
    test_data = loader.get_test_data()
    test_data = rot1.rot1_decrypt(test_data)
    test_data = base64.b64decode(test_data.encode()).decode()

    return json.loads(test_data)


@eel.expose
def submit_action(picked_answers: dict) -> bool or dict or None:
    curr_test = db.get_curr_test_json()
    curr_test_data = get_test_data()

    if curr_test.split('/')[0] == 'testmode':  # picked_answers = { "answer": True | False }
        correct_answer = {k: v for k, v in curr_test_data['answers'].items() if v}
        max_points = curr_test_data['points_per_answer']

        if picked_answers != correct_answer:
            db.dump_progress(0, max_points)
            return correct_answer
        else:
            db.dump_progress(max_points, max_points)
            return None

    elif curr_test.split('/')[0] == 'drag_testmode':  # picked_answers = { "answer": [True | False, position], ... }
        test_data = get_test_data()
        per_answer = curr_test_data['points_per_answer']

        # sifting out wrong answers (wrong answers always have position 0)
        all_right_answers = {answer_text: info for answer_text, info in test_data['answers'].items() if info[1] != 0}

        # sorting by position (the raw test data must be already in right pos since was made)
        # all_right_answers.sort(key=lambda x: x[list(x.keys())[0]][1])

        # compare the answers via the order
        right_counter = 0
        for picked_answer, right_answer in zip(picked_answers, all_right_answers):
            if picked_answer == right_answer:
                right_counter += 1

        db.dump_progress(per_answer * right_counter, per_answer * len(picked_answers.keys()))

        return right_counter != len(picked_answers.keys())
