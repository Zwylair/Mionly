import json
import sqlite3
import settings


def wipe_storage():
    with sqlite3.connect(settings.SQL_DB_FN) as sql:
        cur = sql.cursor()
        cur.execute(settings.SQL_STORAGE_CREATE_SEQ)

        # if the previous test was closed, this will reset its progress to zero
        if cur.execute('SELECT * FROM storage').fetchone():
            cur.execute('DELETE FROM storage')


def dump_chosen_test(ww_book: str, unit: str, test: str):
    with sqlite3.connect(settings.SQL_DB_FN) as sql:
        cur = sql.cursor()
        cur.execute('INSERT INTO storage (test_dir_path) VALUES (?)', (f'{ww_book}/{unit}/{test}',))


def dump_curr_available_tests(curr_test: str, available_tests: list):
    ww_book, unit, test = get_chosen_test()
    available_tests = ';'.join(available_tests) if available_tests else ''

    with sqlite3.connect(settings.SQL_DB_FN) as sql:
        cur = sql.cursor()
        cur.execute(f'UPDATE storage SET available_tests=?, curr_test=? WHERE test_dir_path=?',
                    (available_tests, curr_test, f'{ww_book}/{unit}/{test}'))


def dump_progress(points: int or float, max_points: int or float):
    curr_test = get_curr_test_json()

    with sqlite3.connect(settings.SQL_DB_FN) as sql:
        cur = sql.cursor()

        testing_datas = cur.execute('SELECT testing_datas FROM storage WHERE curr_test=?', (curr_test,)).fetchone()[0]
        testing_datas = json.loads(testing_datas)
        testing_datas['max_points'] += max_points
        testing_datas['got_points'] += points
        testing_datas = json.dumps(testing_datas)

        cur.execute(f'UPDATE storage SET testing_datas=? WHERE curr_test=?', (testing_datas, curr_test))


def dump_progress_results(wrong_answers: int, right_answers: int):
    with sqlite3.connect(settings.SQL_DB_FN) as sql:
        cur = sql.cursor()
        cur.execute('INSERT INTO progress (wrong, right) VALUES (?, ?)',
                    (wrong_answers, right_answers))


def get_chosen_test():
    """Returns list[ww_book, unit, test]"""

    with sqlite3.connect(settings.SQL_DB_FN) as sql:
        cur = sql.cursor()
        result = cur.execute('SELECT * FROM storage').fetchone()

        return result[0].split('/')


def get_curr_available_tests() -> list:
    ww_book, unit, test = get_chosen_test()

    with sqlite3.connect(settings.SQL_DB_FN) as sql:
        cur = sql.cursor()
        available_tests = cur.execute(f'SELECT available_tests FROM storage WHERE test_dir_path="{ww_book}/{unit}/{test}"').fetchone()[0]

        return available_tests.split(';') if available_tests else []


def get_curr_test_json() -> str:
    with sqlite3.connect(settings.SQL_DB_FN) as sql:
        cur = sql.cursor()
        _, curr_test, _, _ = cur.execute('SELECT * FROM storage').fetchone()

        return curr_test


def get_progress() -> dict:  # {test_json: points, ...}
    with sqlite3.connect(settings.SQL_DB_FN) as sql:
        cur = sql.cursor()
        _, _, _, progress = cur.execute('SELECT * FROM storage').fetchone()

        return json.loads(progress)


def get_progress_result() -> dict:
    """Returns {"max_points": int, "got_points": int} """

    with sqlite3.connect(settings.SQL_DB_FN) as sql:
        cur = sql.cursor()
        testing_datas = cur.execute('SELECT testing_datas FROM storage').fetchone()

        return json.loads(testing_datas[0])


def get_completed_tests_count() -> int:
    with sqlite3.connect(settings.SQL_DB_FN) as sql:
        cur = sql.cursor()
        _, _, _, progress = cur.execute('SELECT * FROM storage').fetchone()

        return len(json.loads(progress).keys())
