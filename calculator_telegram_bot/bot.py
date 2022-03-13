from asyncio import Lock, Task, Queue, QueueEmpty, QueueFull, create_task, sleep
from calculator_telegram_bot.client import TelegramBotApiClient
from calculator_telegram_bot.enums import BotState, BotStateSets, Types
from calculator_telegram_bot.decorators import states_allowed
from calculator_telegram_bot.models import (
    TelegramBotAdapters,
    TelegramUpdate
)
from calculator_telegram_bot import errors, settings
from logging import getLogger
from typing import Coroutine, Dict, List, Optional, Type
from uuid import uuid4


class TelegramBot:
    _state = BotState.EMPTY

    def __init__(
        self,
        token: str,
        inbound_events_queue_size: Optional[int] = None,
        update_handler_workers: int = 1,
        update_handlers: Optional[Types.UPDATE_HANDLERS_SET.value] = None
    ):
        super(TelegramBot, self).__init__()
        self.log = getLogger(self.__class__.__name__)
        self.inbound_events_queue_size = (
            inbound_events_queue_size
            if isinstance(inbound_events_queue_size, int)
            else settings.QUEUE_SIZE_INBOUND_EVENTS
        )
        self.update_handler_workers = update_handler_workers
        self.update_handlers = {
            update_type: handler
            for handler, update_types in (update_handlers or {}).items()
            for update_type in update_types
        }
        self.bg_tasks = {}
        self.queue_inbound_events = None
        self.lock_closing = Lock()
        self.token = token
        self._bot_meta = {
            "id": 0,
            "first_name": None,
            "last_name": None,
            "username": "",
            "options": {}
        }
        self._adapters = TelegramBotAdapters(
            {
                "answer_inline_query": self.answer_inline_query,
                "check_auth": self.check_auth,
                "send_message": self.send_message,
                "id": self.id,
            }
        )
        self._client = TelegramBotApiClient(token)
        self.state = BotState.CREATED

    @states_allowed([BotStateSets.READY])
    async def check_auth(self) -> Dict:
        return await self._client.get_me()

    @states_allowed([BotStateSets.WORKING], raise_exc=True, no_log=True)
    async def handle_updates(self) -> None:
        handler_id = str(uuid4()).split("-")[-1]
        self.log.debug(f"Start updates handler {handler_id}")
        while self.state in BotStateSets.WORKING.value:
            if all((
                self.state == BotState.CLOSING,
                self.queue_inbound_events.empty()
            )):
                self.log.debug(f"Stop updates handler {handler_id}")
                break
            update = self.get_update()
            if update and update.type in self.update_handlers:
                self.log.debug(f"Update received: {update.data}")
                handler = self.update_handlers[update.type]
                # FIXME add try-except with on-error and on-success callbacks
                await handler(self.adapters, update)
            await sleep(0.01)

    @states_allowed([BotStateSets.READY])
    async def listen_updates(self, *args, **kwargs) -> None:
        self.state = BotState.RUNNING
        if (
            self.bg_tasks["update_listener"]
            and not self.bg_tasks["update_listener"][0].done()
        ):
            return

        self.bg_tasks["update_listener"] = [self.run_background(
            self._listen_updates(*args, **kwargs)
        )]

    @states_allowed([[BotState.RUNNING]])
    async def pause_updates(self) -> None:
        self.state = BotState.PAUSED

    async def _listen_updates(
        self, limit: Optional[int] = None, timeout: Optional[int] = None
    ) -> None:
        next_id = 0
        while self.state == BotState.RUNNING:
            result = await self.get_updates(
                offset=next_id,
                limit=limit or 100,  # FIXME pick value from config/enums
                timeout=timeout or 1  # FIXME pick value from config/enums
            )

            queue_full_warned = False
            for update in result:
                if self.state != BotState.RUNNING:
                    break
                if self.queue_inbound_events.full() and not queue_full_warned:
                    self.log.warning("Inbound events queue is full")
                    queue_full_warned = True

                while self.state == BotState.RUNNING:
                    try:
                        self.queue_inbound_events.put_nowait(update)
                    except QueueFull:
                        await sleep(0.01)
                        continue
                    else:
                        break

                next_id = update.update_id + 1
                await sleep(0.01)

        await self.get_updates(offset=next_id, limit=1, timeout=0)

    @states_allowed([BotStateSets.WORKING], raise_exc=True, no_log=True)
    def get_update(self) -> Optional[TelegramUpdate]:
        try:
            result = self.queue_inbound_events.get_nowait()
            self.queue_inbound_events.task_done()
            return result
        except (AttributeError, QueueEmpty):
            return

    @states_allowed([BotStateSets.WORKING])
    async def get_updates(self, *args, **kwargs) -> List[TelegramUpdate]:
        return await self._client.get_updates(*args, **kwargs)

    @states_allowed([BotStateSets.READY])
    async def answer_inline_query(self, *args, **kwargs) -> Dict:
        return await self._client.answer_inline_query(*args, **kwargs)

    @states_allowed([BotStateSets.READY])
    async def send_message(self, *args, **kwargs) -> Dict:
        return await self._client.send_message(*args, **kwargs)

    def run_background(self, coro: Coroutine) -> Task:
        return create_task(self.task_wrapper(coro))

    async def task_wrapper(self, coro: Coroutine) -> None:
        try:
            await coro
        except Exception:
            self.log.exception(f"Background task failed: {coro}")
            self.state = BotState.FAILED

    async def cleanup_tasks(
        self, tasks: Optional[Dict[str, List[Task]]] = None
    ) -> None:
        tasks_list = [
            task for t_by_type in (tasks or self.bg_tasks.values())
            for task in t_by_type
        ]
        self.log.debug(
            f"Waiting for {len([x for x in tasks_list if not x.done()])}"
            " running tasks"
        )
        while not all([x.done() for x in tasks_list]):
            await sleep(0.01)

    '''
    Allows to run bot in attached mode.
    '''
    @states_allowed([
        BotStateSets.STOP, [BotState.CREATED, BotState.INITIALIZED]
    ])
    async def run(self) -> None:
        await self.listen_updates()
        while self.state == BotState.RUNNING:
            await sleep(0.01)

    @states_allowed([BotStateSets.STOP, [BotState.CREATED]])
    async def start(self) -> None:
        self.log.info("Starting bot")
        self.queue_inbound_events = Queue(self.inbound_events_queue_size)
        self.bg_tasks = {
            "update_listener": [],
            "update_handlers": [
                self.run_background(self.handle_updates())
                for _ in range(self.update_handler_workers)
            ]
        }
        await self._client.init_session()
        self.state = BotState.INITIALIZED
        self.log.debug("Authorizing")
        bot_meta = await self.check_auth()
        if not bot_meta:
            self.log.warning("Authorization check failed, no data loaded")
            self.state = BotState.FAILED

        self._bot_meta.update({
            "id": bot_meta["id"],
            "first_name": bot_meta.get("first_name"),
            "last_name": bot_meta.get("last_name"),
            "username": bot_meta["username"],
            "options": {
                "inline_queries": bot_meta["supports_inline_queries"],
                "join_groups": bot_meta["can_join_groups"],
                "read_all_group_messages": bot_meta[
                    "can_read_all_group_messages"
                ],
            },
        })

    async def stop(self) -> None:
        if self.state not in BotStateSets.STOP.value:
            async with self.lock_closing:
                self.state = BotState.CLOSING
                self.log.info("Stopping bot")
                await self.queue_inbound_events.join()
                await self.cleanup_tasks()
                await self._client.drop_session()
                self.state = BotState.CLOSED
            return

        self.log.warning("Bot is being stopped or already stopped")

    @property
    def adapters(self) -> TelegramBotAdapters:
        return self._adapters

    @property
    def id(self) -> int:
        return self._bot_meta["id"]

    @property
    def first_name(self) -> Optional[str]:
        return self._bot_meta["first_name"]

    @property
    def last_name(self) -> Optional[str]:
        return self._bot_meta["last_name"]

    @property
    def username(self) -> str:
        return self._bot_meta["username"]

    @property
    def options(self) -> Dict:
        return self._bot_meta["options"]

    @property
    def state(self) -> BotState:
        return self._state

    @state.setter
    def state(self, value: BotState) -> None:
        if self.state != value:
            self.log.debug(f"State change: {self.state.name} -> {value.name}")
            self._state = value

    async def __aenter__(self) -> "TelegramBot":
        await self.start()
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb,
    ) -> None:
        await self.stop()

    def __aiter__(self) -> "TelegramBot":
        return self

    async def __anext__(self) -> TelegramUpdate:
        while True:
            try:
                result = self.get_update()
            except errors.ProhibitedStateError:
                break
            else:
                if result:
                    return result
                await sleep(0.1)

        raise StopAsyncIteration
