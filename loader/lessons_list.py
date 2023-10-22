from typing import List
import os
import eel


@eel.expose
def load_ww_book_list() -> List[str]:
    return os.listdir('tests')


@eel.expose
def load_units_list(ww_book: str) -> List[str]:
    return os.listdir(f'tests/{ww_book}')


@eel.expose
def load_tests_list(ww_book: str, unit: str) -> List[str]:
    return os.listdir(f'tests/{ww_book}/{unit}')
