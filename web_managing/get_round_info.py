import json
# import base64
import os.path
from fastapi import FastAPI
# import rot
import db


def get_full_round_info() -> dict:
    """
    Got round info:
        title: str
        round_text: str
        answers: dict['answer1': ..., 'answer2': ...]
        points_per_correct_answer: int = 1
    """
    path = os.path.join('tests', db.STORAGE.chosen_test_name, db.STORAGE.round_type, db.STORAGE.chosen_round)

    with open(path) as file:
        content = file.read()
    # content = rot.decrypt(content).encode()
    # content = base64.b64decode(content).decode()
    content = json.loads(content)

    return content


def get_round_info() -> dict:
    """
    Got round info:
        title: str
        round_text: str
        answers: dict['answer1': ..., 'answer2': ...]
        points_per_correct_answer: int = 1

    Returned round info:
        round_type: str
        title: str
        round_text: str
        randomize_answers: bool
        answers: ['answer1', 'answer2', ...]
    """
    content = get_full_round_info()
    return_content = {
        'round_type': db.STORAGE.round_type,
        'title': content.get('title'),
        'round_text': content.get('round_text'),
        'randomize_answers': db.STORAGE.randomize_answers,
        'answers': list(content.get('answers').keys())
    }

    return return_content


def get_opened_rounds_count() -> int:
    return db.STORAGE.opened_rounds_count


def get_total_rounds_count() -> int:
    return db.STORAGE.total_rounds_count


def is_this_round_completed() -> bool:
    return f'{db.STORAGE.round_type}/{db.STORAGE.chosen_round}' == db.STORAGE.last_submitted_round


def setup(app: FastAPI):
    app.get('/db/get/round_info')(get_round_info)
    app.get('/db/get/opened_rounds_count')(get_opened_rounds_count)
    app.get('/db/get/total_rounds_count')(get_total_rounds_count)
    app.get('/db/get/is_this_round_completed')(is_this_round_completed)
