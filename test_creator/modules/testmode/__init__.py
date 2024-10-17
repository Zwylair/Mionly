from test_creator.modules.testmode.classes import *
from test_creator.modules.testmode.round_creator import *
from test_creator import classes
from shared_funcs.language import loc
from settings import *
import log

logger = logging.getLogger(__name__)
logging.basicConfig(level=LOGGING_LEVEL, handlers=log.get_handler_for_me())


def setup(test_object_getter_func: Callable[[], classes.Test]):
    logger.debug(f'Setting up {__name__} module. Spawning creator button.')

    round_creator.test_object_getter = test_object_getter_func
    dpg.add_button(label=loc('testmode.__init__.add_round_button'), callback=lambda: open_round_creator())
