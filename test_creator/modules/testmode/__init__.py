from test_creator.modules.testmode.classes import *
from test_creator.modules.testmode.round_creator import *
from test_creator import classes


def setup(test_object_getter_func: Callable[[], classes.Test]):
    round_creator.test_object_getter = test_object_getter_func
    spawn_round_creator_button()


def spawn_round_creator_button():
    dpg.add_button(label='Add testmode round', callback=lambda: open_round_creator())
