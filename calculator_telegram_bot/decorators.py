from calculator_telegram_bot.enums import TelegramBot
from calculator_telegram_bot import errors
from enum import Enum
from inspect import iscoroutinefunction
from logging import getLogger
from typing import List, Union

log = getLogger(__name__)
AllowedStates = List[Union[Enum, List[Enum]]]


def states_allowed(
    states: AllowedStates,
    raise_exc: bool = TelegramBot.RAISE_ON_WRONG_STATE,
    no_log: bool = False
):
    states = [
        x for y in states for x in (y if isinstance(y, list) else y.value)
    ]

    def wrapper(func):
        if iscoroutinefunction(func):
            async def wrapped(self, *args, **kwargs):
                if self.state not in states:
                    msg = (
                        f"Cannot call {func.__name__} "
                        f"in state {self.state.name}"
                    )
                    if not no_log:
                        self.log.error(msg)
                    exc_msg = (
                        f"{msg}. Allowed states: "
                        f"{', '.join([x.name for x in states])}"
                    )
                    if raise_exc:
                        raise errors.ProhibitedStateError(exc_msg)
                    return

                return await func(self, *args, **kwargs)
        else:
            def wrapped(self, *args, **kwargs):
                if self.state not in states:
                    msg = (
                        f"Cannot call {func.__name__} "
                        f"in state {self.state.name}"
                    )
                    if not no_log:
                        self.log.error(msg)
                    exc_msg = (
                        f"{msg}. Allowed states: "
                        f"{', '.join([x.name for x in states])}"
                    )
                    if raise_exc:
                        raise errors.ProhibitedStateError(exc_msg)
                    return

                return func(self, *args, **kwargs)

        return wrapped
    return wrapper
