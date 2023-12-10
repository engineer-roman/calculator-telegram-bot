import logging
from sys import stdout

from loguru import logger  # pylint: disable=E0611
from loguru._logger import Logger

from calculator_bot.config.settings import LogStdSettings


class InterceptHandler(logging.Handler):
    loglevel_mapping = {
        50: "CRITICAL",
        40: "ERROR",
        30: "WARNING",
        20: "INFO",
        10: "DEBUG",
        5: "DEBUG",
        0: "NOTSET",
    }

    def emit(self, record) -> None:  # type: ignore
        try:
            level = logger.level(record.levelname).name
        except (AttributeError, ValueError):
            level = self.loglevel_mapping[record.levelno]

        frame = logging.currentframe()
        depth = 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back  # type: ignore
            depth += 1

        log = logger.bind(request_id="app")
        log.opt(
            depth=depth,
            exception=record.exc_info
        ).log(level, record.getMessage())


def setup_logger(config: LogStdSettings) -> Logger:
    replace_loggers = ("aiogram",)

    logger.remove()
    logger.add(
        stdout,
        level=config.log_level,
        format=config.log_format,
        diagnose=config.rich_exceptions,
    )

    logging.basicConfig(handlers=[InterceptHandler()], level=0)

    for _log in replace_loggers:
        _logger = logging.getLogger(_log)
        _logger.propagate = False
        _logger.handlers = [InterceptHandler()]

    return logger.bind(request_id=None, method=None)  # type: ignore
