import sys

from loguru import logger


def configure_logger():
    logger.remove()
    logger.add(
        sink=sys.stdout,
        diagnose=False,
    )