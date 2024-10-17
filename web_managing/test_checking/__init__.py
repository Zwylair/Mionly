from fastapi import FastAPI
from pydantic import BaseModel
from web_managing.test_checking import testmode, drag_testmode, input_testmode
import db

ROUND_CHECKS = {
    'testmode': testmode.check,
    'drag_testmode': drag_testmode.check,
    'input_testmode': input_testmode.check,
}
VALID_ROUND_TYPES = tuple(ROUND_CHECKS.keys())


class GotAnswers(BaseModel):
    answers: dict | list | str


def check_round_answers(got_answers: GotAnswers) -> dict:
    """
    Got answers:
        testmode: list['answer1', 'answer2', ...]
    """
    db.STORAGE.last_submitted_round = f'{db.STORAGE.round_type}/{db.STORAGE.chosen_round}'
    return ROUND_CHECKS[db.STORAGE.round_type](got_answers.answers)


def setup(app: FastAPI):
    app.post('/db/send_answers')(check_round_answers)
