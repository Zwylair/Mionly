# test_dir_path = 'test/ww_book/unit/test'
# curr_test is a json from test_dir_path
# available_tests = 'test_json;test_json;test_json...'
# test_rewards = '{test_json: points, ...}'
SQL_STORAGE_CREATE_SEQ = """
CREATE TABLE IF NOT EXISTS "storage" (
    "test_dir_path"	TEXT NOT NULL,
    "curr_test"	TEXT,
    "available_tests"	TEXT,
    "testing_datas"  TEXT DEFAULT '{"max_points": 0, "got_points": 0}'
)"""
SQL_DB_FN = 'db.sql'

# EEL
EEL_WEB_DIR = 'web'
EEL_OPTIONS = {
    'mode': 'chrome',
    'port': 8000,
    'size': (800, 600)
}
