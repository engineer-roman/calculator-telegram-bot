import os
import sys
from calculator_telegram_bot.enums import (
    TelegramBot,
    Logging,
    PROJECT_ENV_PREFIX
)
from calculator_telegram_bot.errors import IncorrectSettings
from logging.config import dictConfig

PROJECT_ENV_PREFIX = os.getenv("CALC_TG_BOT_PREFIX", PROJECT_ENV_PREFIX)

# Important settings. Application cannot work without them.
try:
    AUTH_TOKEN = os.environ[f"{PROJECT_ENV_PREFIX}_AUTH_TOKEN"]
except KeyError as err:
    raise IncorrectSettings(f"Failed to find ENV variable {err}")


LOG_ACCESS_MESSAGES = os.getenv(
    f"{PROJECT_ENV_PREFIX}_ACCESS_MESSAGES", Logging.ACCESS_MESSAGES
)
QUEUE_SIZE_INBOUND_EVENTS = os.getenv(
    f"{PROJECT_ENV_PREFIX}_QUEUE_SIZE_INBOUND_EVENTS",
    TelegramBot.QUEUE_SIZE_INBOUND_EVENTS
)


def setup_logging():
    log_formatter = os.getenv(f"{PROJECT_ENV_PREFIX}_LOG_FORMATTER", Logging.FORMATTER)
    log_level = os.getenv(f"{PROJECT_ENV_PREFIX}_LOG_LEVEL", Logging.LEVEL)
    if log_level.lower() not in Logging.LEVELS:
        raise AttributeError(f"Unknown log level: {log_level.lower()}")

    if log_formatter.lower() not in Logging.FORMATTERS:
        raise AttributeError(f"Unknown formatter: {log_formatter.lower()}")

    logging_preset = {
        "version": 1,
        "disable_existing_loggers": True,
        "formatters": {
            log_formatter: Logging.FORMATTERS[log_formatter.lower()]
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": log_formatter,
                "stream": sys.stdout
            },
        },
        "loggers": {
            "": {
                "handlers": ["console"],
                "level": log_level.upper(),
            },
        },
    }
    dictConfig(logging_preset)
    return logging_preset


def configure():
    setup_logging()
