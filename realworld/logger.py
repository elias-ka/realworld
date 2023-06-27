import logging

from realworld.config import LOG_LEVEL

LOG_FORMAT_DEBUG = "%(levelname)s:\t%(message)s:\n\t%(pathname)s:%(funcName)s:%(lineno)d"

level = getattr(logging, str(LOG_LEVEL).upper(), logging.WARNING)


def configure_logging() -> None:
    if level == logging.DEBUG:
        logging.basicConfig(level=level, format=LOG_FORMAT_DEBUG)
    else:
        logging.basicConfig(level=level)


logger = logging.getLogger("realworld")
