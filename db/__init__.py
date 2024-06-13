from dataclasses import dataclass

import fastapi
from fastapi import FastAPI


@dataclass
class Storage:
    chosen_test_name: str
    round_type: str | None
    chosen_round: str | None
    randomize_rounds: bool
    randomize_answers: bool
    available_rounds: dict
    allowed_round_types: tuple
    total_rounds_count: int
    last_submitted_round: str | None
    points: int = 0
    max_points: int = 0
    opened_rounds_count: int = 0


STORAGE: Storage | None = None


def wipe_storage():
    global STORAGE
    STORAGE = None


def get_storage():
    if not STORAGE.available_rounds and STORAGE.chosen_round is None:
        return STORAGE
    raise fastapi.HTTPException(403)


def setup(app: FastAPI):
    app.get('/db/wipe')(wipe_storage)
    app.get('/db/get/storage')(get_storage)
