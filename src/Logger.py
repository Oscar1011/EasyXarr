from logging import error
from loguru import logger

logger.add('log/EasyXarr_{time}.log', rotation='00:00')


def info(Text):
    # logger.info(Text)
    pass


def success(Text):
    logger.success(Text)


def error(Text):
    logger.error(Text)


def warning(Text):
    logger.warning(Text)
