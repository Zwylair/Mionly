from web_managing.get_round_info import get_full_round_info
import db


def check(got_answers: list[str]):
    """
    Got round info:
        title: str
        round_text: str
        answers: ['answer1', 'answer2', ...]
        points_per_correct_answer: float

    Got answers:
        ['written_answer1', 'written_answer2', ...]

    Return info:
        correct_answers: {'correct_answer1': true/false, 'correct_answer2': true/false, ...}
        got_points: float
        max_points: float
    """

    print(f'got_answers: {got_answers}')

    round_info = get_full_round_info()
    answers: list[str] = round_info.get('answers')
    points_per_correct_answer: float = round_info.get('points_per_correct_answer')

    correct_answers = {}
    max_round_points = 0.0
    got_round_points = 0.0

    for got_answer, right_answer in zip(got_answers, answers):
        max_round_points += points_per_correct_answer

        if got_answer.lower() == right_answer.lower():
            correct_answers[right_answer] = True
            got_round_points += points_per_correct_answer
        else:
            correct_answers[right_answer] = False

    db.STORAGE.max_points += max_round_points
    db.STORAGE.points += got_round_points

    return_info = {
        'correct_answers': correct_answers,
        'got_points': got_round_points,
        'max_points': max_round_points,
    }

    return return_info
