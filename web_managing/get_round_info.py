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
    path = os.path.join(db.STORAGE.test_root, db.STORAGE.chosen_round)

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
        points_per_correct_answer: float = 1.0

    Returned round info:
        round_type: str
        title: str
        round_text: str
        randomize_answers: bool
        answers: ['answer1', 'answer2', ...]
        round_counter_text: str
    """
    content = get_full_round_info()
    answers = content.get('answers')

    if isinstance(answers, dict):
        answers = list(answers.keys())
    elif isinstance(answers, list):
        pass  # answers = answers

    return_content = {
        'round_type': db.STORAGE.round_type,
        'title': content.get('title'),
        'round_text': content.get('round_text'),
        'randomize_answers': db.STORAGE.randomize_answers,
        'answers': answers,
        'round_counter_text': f'{db.STORAGE.opened_rounds_count}/{db.STORAGE.total_rounds_count}',
    }

    return return_content


def is_this_round_completed() -> bool:
    return f'{db.STORAGE.round_type}/{db.STORAGE.chosen_round}' == db.STORAGE.last_submitted_round


def setup(app: FastAPI):
    app.get('/db/get/round_info')(get_round_info)
    app.get('/db/get/is_this_round_completed')(is_this_round_completed)
