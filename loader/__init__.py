import base64
import json
import hashlib
import os
import eel
import db
import rot1
from loader import lessons_list


def data_decode(test_data: str) -> dict:
    test_data = rot1.rot1_decrypt(test_data)
    test_data = base64.b64decode(test_data.encode()).decode()
    return json.loads(test_data)


def data_encode(test_data: dict) -> str:
    test_data = json.dumps(test_data)
    test_data = base64.b64encode(test_data.encode()).decode()
    return rot1.rot1_encrypt(test_data)


def gen_rand_hash() -> str:
    return hashlib.sha256(os.urandom(32)).hexdigest()[:16]


@eel.expose
def get_test_data() -> str:
    ww_book, unit, test = db.get_chosen_test()
    curr_test = db.get_curr_test_json()

    with open(f'tests/{ww_book}/{unit}/{test}/{curr_test}') as file:
        test_content = file.read()

    if curr_test.split('/')[0] == 'write_heard':
        parsed = data_decode(test_content)

        # saving temp audio file
        out_audio_fn = f'temp/{gen_rand_hash()}.mp3'

        with open(f'web/{out_audio_fn}', 'wb') as file:
            file.write(base64.b64decode(parsed['coded_audio']))

        parsed['audio_path'] = out_audio_fn
        test_content = data_encode(parsed)

    return test_content
