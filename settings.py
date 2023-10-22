# test_dir_path = 'test/ww_book/unit/test'
# curr_test is a json from test_dir_path
# available_tests = 'test_json;test_json;test_json...'
# test_rewards = '{test_json: points, ...}'
SQL_CREATE_SEQUENCES = ["""
CREATE TABLE IF NOT EXISTS "storage" (
    "test_dir_path"	TEXT NOT NULL,
    "curr_test"	TEXT,
    "available_tests"	TEXT,
    "test_rewards"  TEXT DEFAULT '{}'
)""", """
CREATE TABLE IF NOT EXISTS "progress" (
    "wrong"	INTEGER NOT NULL,
    "right"	INTEGER NOT NULL
)"""]

SQL_DB_FN = 'db.sql'

# IMPORTANT TO CHANGE
TEST_JSON_TO_WEBPAGE = {
    'testmode.json': '/testmode.html'
}
MAX_TEST_REWARDS = {  # 1 point per 1 answer
    'testmode.json': 1
}

# EEL
EEL_WEB_DIR = 'web'
EEL_OPTIONS = {
    'mode': 'chrome',
    'port': 8000,
    'size': (800, 600)
}
