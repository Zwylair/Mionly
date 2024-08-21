import os.path
import logging

WEB_DIR = 'web'
HOST_URL = '127.0.0.1'
HOST_PORT = 8000
LOGGING_FORMAT = '[%(name)s.%(funcName)s]: [%(levelname)s] %(message)s'
LOGGING_LEVEL = logging.DEBUG
TEST_CREATOR_DATA_PATH = 'test_creator.data'
LANGUAGE_FILE_NAME = os.path.join(TEST_CREATOR_DATA_PATH, 'language.json')
TEST_CREATOR_LOCK_FILENAME = os.path.join(TEST_CREATOR_DATA_PATH, 'test_creator.lock')
