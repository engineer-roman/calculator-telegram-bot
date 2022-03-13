#!/usr/local/python3
import functools
import signal

from asyncio import get_event_loop
from calculator_telegram_bot.settings import AUTH_TOKEN
from calculator_telegram_bot.bot import TelegramBot
from calculator_telegram_bot.enums import BotState, TelegramUpdateTypes
from calculator_telegram_bot.handlers import message_handler, inline_handler

loop = get_event_loop()


def stop_callback(bot: TelegramBot) -> None:
    bot.state = BotState.FAILED


async def run() -> None:
    async with TelegramBot(
        AUTH_TOKEN,
        update_handlers={
            message_handler: [TelegramUpdateTypes.MESSAGE],
            inline_handler: [TelegramUpdateTypes.INLINE_QUERY]
        }
    ) as bot:
        loop.add_signal_handler(
            signal.SIGTERM, functools.partial(stop_callback, bot)
        )
        await bot.run()


if __name__ == '__main__':
    loop.run_until_complete(run())
