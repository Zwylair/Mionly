import os
from dataclasses import dataclass
from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from settings import *


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
    points: float = 0
    max_points: float = 0
    opened_rounds_count: int = 0
    test_source_root: str | None = None


STORAGE: Storage | None = None


def wipe_storage():
    global STORAGE
    STORAGE = None


def get_storage():
    if not STORAGE.available_rounds and STORAGE.chosen_round is None:
        return STORAGE
    raise HTTPException(403)


async def upload_file(file: UploadFile):
    os.makedirs(WEB_CACHE_PATH, exist_ok=True)

    with open(os.path.join(WEB_CACHE_PATH, file.filename), 'wb') as f:
        content = await file.read()
        f.write(content)

    return JSONResponse({'filename': file.filename})


def setup(app: FastAPI):
    app.get('/db/wipe')(wipe_storage)
    app.get('/db/get/storage')(get_storage)
    app.post('/db/upload_file')(upload_file)
