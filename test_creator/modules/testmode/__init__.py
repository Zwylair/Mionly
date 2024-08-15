from test_creator.modules.testmode.classes import *
from test_creator.modules.testmode.round_creator import *
from test_creator import classes
from settings import *

logger = logging.getLogger(__name__)
logging.basicConfig(format=LOGGING_FORMAT)
logger.setLevel(LOGGING_LEVEL)


def setup(test_object_getter_func: Callable[[], classes.Test]):
    logger.debug(f'Setting up {__name__} module. Spawning creator button.')

    round_creator.test_object_getter = test_object_getter_func
    dpg.add_button(label='Add testmode round', callback=lambda: open_round_creator())
