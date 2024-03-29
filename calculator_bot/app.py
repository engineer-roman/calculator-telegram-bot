import asyncio
import sys

import sentry_sdk
import uvloop
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from loguru import logger as log
from prometheus_client import start_http_server

from calculator_bot import entrypoints
from calculator_bot.config.settings import init_settings, Settings
from calculator_bot.libs.doppler import set_env_vars
from calculator_bot.libs.logging import setup_logger


def setup_metrics(metrics_port: int | None) -> None:
    if metrics_port:
        log.info(f"Starting metrics server on port {metrics_port}")
        start_http_server(addr="localhost", port=metrics_port)


def setup_sentry(settings: Settings) -> None:
    if settings.sentry.dsn:
        sentry_sdk.init(
            dsn=settings.sentry.dsn,
            sample_rate=settings.sentry.sample_rate,
            environment=settings.application.release_stage,
            release=settings.application.version,
        )

async def __main() -> bool:
    set_env_vars(False)
    settings = init_settings()
    app_settings = settings.application

    setup_sentry(settings)
    setup_logger(settings.logstd)
    setup_metrics(settings.application.metrics_port)
    log.info(f"Starting calculator-bot version {app_settings.version} in {app_settings.release_stage} environment")

    bot = Bot(token=settings.telegram.bot_api_token)
    dispatcher = Dispatcher()

    dispatcher.message.register(entrypoints.ping_cmd, Command("ping"))
    dispatcher.message.register(entrypoints.start_cmd, Command("start"))
    dispatcher.message.register(entrypoints.help_cmd, Command("help"))
    dispatcher.message.register(entrypoints.direct_query)
    dispatcher.inline_query.register(entrypoints.inline_query)

    log.info("Connecting to TG API")
    try:
        await dispatcher.start_polling(bot)
    except Exception as exc:  # pylint: disable=W0703
        log.exception("Polling failed", exc)
        return False
    return True


def setup_asyncio() -> None:
    uvloop.install()


def main() -> bool:
    setup_asyncio()
    return asyncio.run(__main())


if __name__ == "__main__":
    if main():
        sys.exit(1)
    sys.exit(0)
