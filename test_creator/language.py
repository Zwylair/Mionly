import json
import os.path
from pathlib import Path
from settings import *
import log

logger = logging.getLogger(__name__)
logging.basicConfig(level=LOGGING_LEVEL, handlers=[log.ColorHandler()])


def get_available_languages():
    global all_languages_datas
    languages_root_path = os.path.join(TEST_CREATOR_DATA_PATH, 'languages')

    try:
        all_languages_datas = {}
        for lang in os.listdir(languages_root_path):
            all_languages_datas |= {Path(lang).stem: json.load(open(os.path.join(languages_root_path, lang), encoding='utf8'))}
    except json.JSONDecodeError as _e:
        logger.exception('Failed to load saved language:', exc_info=_e)

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

try:
    chosen_language: str = json.load(open(LANGUAGE_FILE_NAME)).get('language')
except json.JSONDecodeError as e:
    logger.exception('Failed to load saved language:', exc_info=e)
    chosen_language = 'en-GB'

all_languages_datas = {}
get_available_languages()
