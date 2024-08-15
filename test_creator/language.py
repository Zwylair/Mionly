import json
import os.path
from pathlib import Path
from settings import *

logger = logging.getLogger(__name__)
logging.basicConfig(format=LOGGING_FORMAT)
logger.setLevel(LOGGING_LEVEL)


def get_available_languages():
    global all_languages_datas

    all_languages_datas = {}
    for lang in os.listdir('languages/'):
        all_languages_datas |= {Path(lang).stem: json.load(open(f'languages/{lang}', encoding='utf8'))}

    return list(all_languages_datas.keys())


def set_language(lang: str):
    global chosen_language

    if lang not in all_languages_datas.keys():
        logger.info(f'Tried to load missing language: {lang}. Skipping')
        return

    json.dump({'language': lang}, open(LANGUAGE_FILE_NAME, 'w'))
    chosen_language = lang
    logger.debug(f'Set new language: {lang}')


def loc(translation_key: str):
    return all_languages_datas.get(chosen_language, {}).get(translation_key, translation_key)


if not os.path.exists(LANGUAGE_FILE_NAME):
    json.dump({'language': 'en-GB'}, open(LANGUAGE_FILE_NAME, 'w'))

chosen_language: str = json.load(open(LANGUAGE_FILE_NAME)).get('language')
all_languages_datas = {}
get_available_languages()
