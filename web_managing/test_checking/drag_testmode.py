from web_managing.get_round_info import get_full_round_info
import db


def check(got_answers: dict[str, int]):
    """
    Got round info:
        title: str
        round_text: str
        answers: {'answer1': [true/false, position], 'answer2': [true/false, position], ...}
        points_per_correct_answer: int

    Got answers:
        {'picked_answer1': position, 'picked_answer2': position, ...}

    Return info:
        correct_answers: {'correct_answer1': true/false, 'correct_answer2': true/false, ...}
        got_points: int
        max_points: int
    """

    round_info = get_full_round_info()
    answers: dict[str, list[bool, int]] = round_info.get('answers')
    points_per_correct_answer: int = round_info.get('points_per_correct_answer')
    position_to_correct_answer: dict[int, str] = {v[1]: k for k, v in answers.items() if v[1] != 0}

    correct_answers = {}
    max_round_points = 0
    got_round_points = 0

    for got_answer, got_position in got_answers.items():
        max_round_points += points_per_correct_answer

        if answers[got_answer][1] == got_position:
            correct_answers[got_answer] = True
            got_round_points += points_per_correct_answer
        else:
            correct_answer_on_this_position = position_to_correct_answer[got_position]
            correct_answers[correct_answer_on_this_position] = False

    db.STORAGE.max_points += max_round_points
    db.STORAGE.points += got_round_points

    return_info = {
        'correct_answers': correct_answers,
        'got_points': got_round_points,
        'max_points': max_round_points,
    }

    return return_info
