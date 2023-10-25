import eel
import settings
import loader
import db_operations


@eel.expose
def submit_action(picked_answers: list):
    curr_test = db_operations.get_curr_test_json()
    max_points = settings.MAX_TEST_REWARDS[curr_test]

    if curr_test == 'testmode.json':  # picked_answers = [ {"answer": True | False}, ... ]
        wrong_picked_answers = [i for i in picked_answers if not list(i.values())[0]]
        db_operations.dump_progress(max_points - len(wrong_picked_answers))
    elif curr_test == 'drag_testmode.json':  # picked_answers = [ {"answer": [True | False, position]}, ... ]
        all_truly_answers = [item for item in loader.get_test_data()['answers'] if item[list(item.keys())[0]][1] != 0]
        all_truly_answers.sort(key=lambda x: x[list(x.keys())[0]][1])

        wrong_picked_answers = 0
        for picked_answer, true_answer in zip(picked_answers, all_truly_answers):
            if picked_answer != true_answer:
                print(f'not equal: {picked_answer}, {true_answer}')
                wrong_picked_answers += 1
            else:
                print(f'is equal: {picked_answer}, {true_answer}')

        db_operations.dump_progress(max_points - wrong_picked_answers)
