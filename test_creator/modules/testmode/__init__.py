from test_creator.modules.testmode.classes import *
from test_creator.modules.testmode.round_creator import *
from test_creator import classes


def setup(test_obj: classes.Test):
    round_creator.test_object = test_obj
    spawn_round_creator_button()


def spawn_round_creator_button():
    dpg.add_button(label='Add testmode round', callback=lambda: open_round_creator())
