from web_managing.get_round_info import get_full_round_info
import db


def check(got_answer: str):
    """
    Got round info:
        title: str
        round_text: str
        answers: {'answer1': true/false, 'answer2': true/false, ...}
        points_per_correct_answer: float

    Got answers:
        'picked_answer1'

    Return info:
        correct_answers: {'correct_answer1': do you picked correctly (true/false)}
        got_points: float
        max_points: float
    """

    round_info = get_full_round_info()
    answers: dict[str, bool] = round_info.get('answers')
    points_per_correct_answer: float = round_info.get('points_per_correct_answer')

    correct_answers = {}
    got_round_points = 0.0

    db.STORAGE.max_points += points_per_correct_answer

    if answers[got_answer]:  # got_answer = correct_answer
        correct_answers[got_answer] = True
        db.STORAGE.points += points_per_correct_answer
        got_round_points += points_per_correct_answer
    else:
        correct_answer = {v: k for k, v in answers.items()}[True]
        correct_answers[correct_answer] = False

    return_info = {
        'correct_answers': correct_answers,
        'got_points': got_round_points,
        'max_points': points_per_correct_answer,
    }

    return return_info
