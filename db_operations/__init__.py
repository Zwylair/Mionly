import json
import sqlite3
import settings


def dump_chosen_test(ww_book: str, unit: str, test: str):
    with sqlite3.connect(settings.SQL_DB_FN) as sql:
        cur = sql.cursor()
        cur.execute('INSERT INTO storage (test_dir_path) VALUES (?)', (f'{ww_book}/{unit}/{test}',))


def dump_curr_available_tests(curr_test: str, available_tests: list):
    ww_book, unit, test = get_chosen_test()

    with sqlite3.connect(settings.SQL_DB_FN) as sql:
        cur = sql.cursor()
        cur.execute(f'UPDATE storage SET available_tests=?, curr_test=? WHERE test_dir_path=?',
                    (';'.join(available_tests), curr_test, f'{ww_book}/{unit}/{test}'))


def dump_progress(points: int):
    curr_test = get_curr_test_json()

    with sqlite3.connect(settings.SQL_DB_FN) as sql:
        cur = sql.cursor()
        test_rewards = cur.execute('SELECT test_rewards FROM storage WHERE curr_test=?', (curr_test,)).fetchone()[0]
        test_rewards = json.loads(test_rewards)
        test_rewards.update({curr_test: points})
        test_rewards = json.dumps(test_rewards)

        cur.execute(f'UPDATE storage SET test_rewards=? WHERE curr_test=?', (test_rewards, curr_test))


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

        return available_tests.split(';')


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
    """Returns {"wrong": int, "right": int} """

    with sqlite3.connect(settings.SQL_DB_FN) as sql:
        cur = sql.cursor()
        wrong, right = cur.execute('SELECT * FROM progress').fetchone()

        return {"wrong": wrong, "right": right}
