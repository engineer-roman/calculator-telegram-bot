from aiohttp import ClientResponse
from calculator_telegram_bot.enums import (
    CalcActions,
    TelegramUpdateTypes,
    Types
)
from typing import Any, Callable, Dict, List, Optional, Union


class CalcQueryAction(str):
    def __new__(cls, value, start, end, priority):
        cls = str.__new__(CalcQueryAction, value)
        cls.start = start
        cls.end = end
        cls.priority = priority
        cls.callback = CalcActions.CALLBACK_MAPPING[value]
        return cls

    def __lt__(self, value: "CalcQueryAction") -> bool:
        return self.priority < value.priority

    def __gt__(self, value: "CalcQueryAction") -> bool:
        return self.priority > value.priority

    def __eq__(self, value: "CalcQueryAction") -> bool:
        return self.priority == value.priority


class CalcQueryDigit(float):
    def __new__(cls, value, start, end):
        super(CalcQueryDigit, cls).__new__(cls, value)
        cls = float.__new__(CalcQueryDigit, value)
        cls.start = start
        cls.end = end
        return cls


class TelegramBotAdapters:
    def __init__(self, interfaces: Dict[str, Callable]):
        [setattr(self, name, method) for name, method in interfaces.items()]


class Model:
    _fields = []

    def values(self) -> Dict[str, Any]:
        return {x: getattr(self, x) for x in self._fields}


class ApiResponse:
    def __init__(
        self,
        response: ClientResponse,
        time_read_body: Union[float, int],
        time_total: Union[float, int],
        data: Optional[Types.API_RESPONSE_DATA.value] = None
    ):
        self.cookies = response.cookies
        self.headers = response.headers
        self.status = response.status
        self.reason = response.reason
        self.load_error = data if isinstance(data, BaseException) else None
        self.data = data if not isinstance(data, BaseException) else None
        self.time_read_body = time_read_body
        self.time_total = time_total
        self.time_request = time_total - time_read_body


class TelegramApiResponse(ApiResponse):
    pass


class TelegramUpdate:
    def __init__(self, data: Dict):
        self.data = data
        self.update_id = data["update_id"]
        self.type = self._pick_type(data)

    @staticmethod
    def _pick_type(data: Dict) -> TelegramUpdateTypes:
        for update_type in TelegramUpdateTypes:
            if update_type.value in data:
                return update_type

        return TelegramUpdateTypes.UNKNOWN


# FIXME it's part of Update
# class TelegramInlineQuery(Model):
#     def __init__(self, data: Dict):
#         payload = data["inline_query"]
#         self._fields = [
#             "id",
#             "query",
#             "offset"
#         ]
#         [setattr(self, fld, payload[fld]) for fld in self._fields]
#         self._from = payload["from"]


class InputTextMessageContent(Model):
    def __init__(
        self,
        message_text: str,
        parse_mode: Optional[str] = None,
        entities: Optional[List[str]] = None,
        disable_web_page_preview: Optional[bool] = None
    ):
        self._fields = [
            "message_text"
        ]
        self.message_text = message_text
        if parse_mode:
            self.parse_mode = parse_mode
            self._fields.append("parse_mode")
        if entities:
            self.entities = entities
            self._fields.append("parse_mode")
        if disable_web_page_preview:
            self.disable_web_page_preview = disable_web_page_preview
            self._fields.append("parse_mode")


# FIXME add all arguments support
class InlineQueryResultArticle(Model):
    def __init__(
        self,
        query_id: Union[float, int, str],
        title: str,
        input_message_content: InputTextMessageContent,
        # reply_markup,
        # url,
        # hide_url,
        # description,
        # thumb_url,
        # thumb_width,
        # thumb_height
    ):
        self._fields = [
            "type",
            "id",
            "title",
            "input_message_content"
        ]
        self.type = "article"
        self.id = query_id
        self.title = title
        self.input_message_content = input_message_content.values()
