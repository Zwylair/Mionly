import sys
from settings import *


def get_handler_for_me():
    return [ColorHandler()]


class ColorHandler(logging.StreamHandler):
    # https://en.wikipedia.org/wiki/ANSI_escape_code#Colors
    GRAY8 = '38;5;8'
    GRAY7 = '38;5;7'
    ORANGE = '33'
    RED = '31'
    WHITE = '0'

    def __init__(self):
        super().__init__()
        self.setFormatter(logging.Formatter(fmt=LOGGING_FORMAT))

    def emit(self, record):
        if sys.stdout is None:
            return

        # We don't use white for any logging, to help distinguish from user print statements
        level_color_map = {
            logging.DEBUG: self.GRAY8,
            logging.INFO: self.GRAY7,
            logging.WARNING: self.ORANGE,
            logging.ERROR: self.RED,
        }

        csi = f'{chr(27)}['  # control sequence introducer
        color = level_color_map.get(record.levelno, self.WHITE)
        message = self.format(record)

        self.stream.write(f'{csi}{color}m{message}{csi}m\n')


class LogHandler(logging.StreamHandler):
    def __init__(self):
        super().__init__()
        self.setFormatter(logging.Formatter(fmt=LOGGING_FORMAT))

    def emit(self, record):
        if sys.stdout is None:
            return

        self.stream.write(self.format(record))
