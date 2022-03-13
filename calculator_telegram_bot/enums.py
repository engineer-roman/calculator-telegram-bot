import operator
from enum import Enum
from typing import Callable, Dict, List, Union

PROJECT_ENV_PREFIX = "CALC_TG_BOT"


class BotState(Enum):
    EMPTY = 0
    CREATED = 1
    INITIALIZED = 2
    RUNNING = 3
    PAUSED = 4
    CLOSING = 5
    CLOSED = 6
    FAILED = 7
    TERMINATED = 8


class BotStateSets(Enum):
    READY = (BotState.INITIALIZED, BotState.RUNNING, BotState.PAUSED)
    WORKING = (
        BotState.INITIALIZED,
        BotState.RUNNING,
        BotState.PAUSED,
        BotState.CLOSING,
        BotState.FAILED
    )
    STOP = (BotState.CLOSING, BotState.CLOSED, BotState.TERMINATED)
    NO_ITER = (BotState.CLOSED, BotState.CREATED, BotState.EMPTY)


class CalcSettings:
    PARENTHESES_LIMIT = 1000


class CalcActions:
    SUMMARIZE = "+"
    DIFFERENCE = "-"
    MULTIPLY = "*"
    DIVISION = "/"
    FLOOR_DIVISION = "//"
    EXPONENT = "^"
    CALLBACK_MAPPING = {
        SUMMARIZE: operator.add,
        DIFFERENCE: operator.sub,
        MULTIPLY: operator.mul,
        DIVISION: operator.truediv,
        FLOOR_DIVISION: operator.floordiv,
        EXPONENT: operator.pow,
    }
    PRIORITY_MAPPING = {
        SUMMARIZE: 1,
        DIFFERENCE: 1,
        MULTIPLY: 2,
        DIVISION: 2,
        FLOOR_DIVISION: 2,
        EXPONENT: 3,
    }
    SYMBOLS_LIST = (
        SUMMARIZE,
        DIFFERENCE,
        MULTIPLY,
        DIVISION,
        EXPONENT
    )


CALC_DIGIT_SYMBOLS = {*[str(x) for x in range(10)], "."}


class HttpClient:
    SCHEMAS = ("http", "https")
    HEADERS = {"Content-type": "application/json"}
    URL_SCHEMA_TEMPLATED = "{schema}://{base_url}"
    # FIXME Add timeouts here


class TelegramUpdateTypes(Enum):
    MESSAGE = "message"
    EDITED_MESSAGE = "edited_message"
    CHANNEL_POST = "channel_post"
    EDITED_CHANNEL_POST = "edited_channel_post"
    INLINE_QUERY = "inline_query"
    CHOSEN_INLINE_RESULT = "chosen_inline_result"
    CALLBACK_QUERY = "callback_query"
    SHIPPING_QUERY = "shipping_query"
    PRE_CHECKOUT_QUERY = "pre_checkout_query"
    POLL = "poll"
    POLL_ANSWER = "poll_answer"
    MY_CHAT_MEMBER = "my_chat_member"
    UNKNOWN = "unknown"


class TelegramAPI:
    BASE_URL = "api.telegram.org"
    URL_ROOT_TEMPLATED = "{base_url}/bot{token}"
    UPDATE_OBJECT_TYPES = TelegramUpdateTypes


class TelegramBot:
    RAISE_ON_WRONG_STATE = False
    QUEUE_SIZE_INBOUND_EVENTS = 1000


class Logging:
    LEVELS = ("debug", "info", "warning", "error")
    LEVEL = "info"
    FORMATTERS = {
        "plain": {
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S:%s"
        },
    }
    FORMATTER = "plain"
    ACCESS_MESSAGES = True


class Types(Enum):
    API_RESPONSE_DATA = Union[Dict, List[Dict]]
    UPDATE_HANDLERS_SET = Dict[Callable, List[TelegramUpdateTypes]]
    CALC_NUMBER = Union[float, int]
