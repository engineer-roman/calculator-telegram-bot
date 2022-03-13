from aiohttp import ClientResponse, ClientSession
from calculator_telegram_bot.errors import NoHttpSessionAvailable
from calculator_telegram_bot.enums import HttpClient, TelegramAPI, Types
from calculator_telegram_bot.models import (
    ApiResponse,
    TelegramUpdate
)
from logging import getLogger
from time import time
from typing import Dict, List, Optional, Tuple, Type, Union


class ApiClient:
    def __init__(
        self,
        base_url: str,
        schema: str = "https",
        headers: Optional[Dict] = None,
        response_encoding: str = "utf-8"
    ):
        self.log = getLogger(self.__class__.__name__)
        if schema not in HttpClient.SCHEMAS:
            raise AttributeError(f"Incorrect URL schema: {schema}")

        self.schema = schema
        self.base_url = HttpClient.URL_SCHEMA_TEMPLATED.format(
            schema=schema, base_url=base_url
        )
        self.headers = headers or HttpClient.HEADERS
        self.response_encoding = response_encoding
        self.session = None

    async def init_session(
        self, headers: Optional[Dict] = None
    ) -> ClientSession:
        headers = headers or {}
        self.session = ClientSession(headers={**self.headers, **headers})
        return self.session

    async def drop_session(self) -> None:
        if self.session and not self.session.closed:
            await self.session.close()

    async def validate(self, response: ClientResponse) -> bool:
        pass

    async def send_request(
        self,
        endpoint: str,
        method: str,
        *args,
        **kwargs
    ) -> Tuple[ClientResponse, Types.API_RESPONSE_DATA.value, float]:
        if not self.session:
            raise NoHttpSessionAvailable("No active HTTP session found")

        url = self.base_url + endpoint
        self.log.debug(f"{method.upper()} to {endpoint}")
        async with getattr(self.session, method)(
            url, *args, **kwargs
        ) as response:
            time_start = time()
            try:
                data = await response.json(encoding=self.response_encoding)
            except Exception as exc:
                data = exc
            return response, data, time() - time_start

    async def send(
        self,
        endpoint: str,
        method: str,
        retries_limit: Optional[int] = None,
        retry_timeout: Optional[int] = None,
        *args,
        **kwargs
    ) -> ApiResponse:
        # FIXME add backoff handling
        time_start = time()
        response, data, time_read_body = await self.send_request(
            endpoint, method, *args, **kwargs
        )
        return ApiResponse(response, time_read_body, time() - time_start, data)

    async def __aenter__(self) -> "ApiClient":
        await self.init_session()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb,
    ) -> None:
        await self.drop_session()


class TelegramBotApiClient(ApiClient):
    def __init__(
        self, token: str, base_url: Optional[str] = None, *args, **kwargs
    ):
        base_url = base_url or TelegramAPI.BASE_URL
        super(TelegramBotApiClient, self).__init__(base_url, *args, **kwargs)
        self.base_url = TelegramAPI.URL_ROOT_TEMPLATED.format(
            base_url=self.base_url, token=token
        )

    async def get_updates(
        self,
        limit: int = 100,
        timeout: int = 0,
        offset: Optional[int] = None,
        allowed_updates: Optional[List[str]] = None
    ) -> List[TelegramUpdate]:
        endpoint = "/getUpdates"
        method = "get"
        allowed_updates = allowed_updates or []
        params = {
            "limit": limit,
            "timeout": timeout,
            "allowed_updates": allowed_updates,
        }
        if offset:
            params["offset"] = offset

        result = await self.query(endpoint, method, params=params)
        return [
            TelegramUpdate(x)
            for x in ([] if not result else result["result"])
        ]

    async def get_me(self) -> Optional[Dict]:
        endpoint = "/getMe"
        method = "get"
        response = await self.query(endpoint, method)
        return {} if not response else response["result"]

    async def answer_inline_query(
        self,
        inline_query_id: str,
        results: List[Dict],
        cache_time: int = 300,
        is_personal: bool = False,
        next_offset: str = "",
        switch_pm_text: Optional[str] = None,
        switch_pm_parameter: Optional[str] = None
    ) -> Dict:
        endpoint = "/answerInlineQuery"
        method = "post"
        payload = {
            "inline_query_id": inline_query_id,
            "results": results,
            "cache_time": cache_time,
            "is_personal": is_personal,
            "next_offset": next_offset,
        }
        if switch_pm_text:
            payload["switch_pm_text"] = switch_pm_text
        if switch_pm_parameter:
            payload["switch_pm_parameter"] = switch_pm_parameter
        response = await self.query(endpoint, method, json=payload)
        return {} if not response else response["result"]

    async def send_message(
        self,
        chat_id: Union[int, str],
        text: str,
        disable_web_page_preview: bool = False,
        disable_notification: bool = False,
        reply_to_message_id: Optional[int] = None,
        allow_sending_without_reply: bool = False,
    ) -> Dict:
        endpoint = "/sendMessage"
        method = "post"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "disable_web_page_preview": disable_web_page_preview,
            "disable_notification": disable_notification,
            "allow_sending_without_reply": allow_sending_without_reply
        }
        if reply_to_message_id:
            payload["reply_to_message_id"] = reply_to_message_id
        response = await self.query(endpoint, method, json=payload)
        return {} if not response else response["result"]

    async def query(self, *args, **kwargs) -> Types.API_RESPONSE_DATA:
        response = await self.send(*args, **kwargs)
        if isinstance(response.load_error, BaseException):
            raise response.load_error

        return self.validate(response)

    def validate(self, response: ApiResponse) -> Optional[Union[List, Dict]]:
        return response.data
