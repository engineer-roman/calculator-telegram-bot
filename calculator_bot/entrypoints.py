from uuid import uuid4

from aiogram.types import (InlineQuery, InlineQueryResultArticle,
                           InputTextMessageContent, Message)

from calculator_bot.config.settings import init_application_settings
from calculator_bot.libs.const.messages import (HELP_MESSAGE,
                                                META_MESSAGE_TEMPLATE,
                                                WELCOME_MESSAGE)
from calculator_bot.query_processor import QueryProcessor

app_settings = init_application_settings()


async def ping_cmd(message: Message) -> None:
    meta_msg = META_MESSAGE_TEMPLATE.format(version=app_settings.version)
    response = f"{WELCOME_MESSAGE}\n\n{meta_msg}"
    await message.answer(response)


async def start_cmd(message: Message) -> None:
    meta_msg = META_MESSAGE_TEMPLATE.format(version=app_settings.version)
    response = f"{WELCOME_MESSAGE}\n\n{HELP_MESSAGE}\n\n{meta_msg}"
    await message.answer(response)


async def help_cmd(message: Message) -> None:
    meta_msg = META_MESSAGE_TEMPLATE.format(version=app_settings.version)
    response = f"{HELP_MESSAGE}\n---\n{meta_msg}"
    await message.answer(response)


async def direct_query(message: Message) -> None:
    response = f"{message.text} = {message.text}"
    await message.reply(response)


async def inline_query(query: InlineQuery) -> None:
    query_result = await QueryProcessor(app_settings.parentheses_limit).process(query.query)

    result = InlineQueryResultArticle(
        id=uuid4().hex,
        title=query_result.result,
        input_message_content=InputTextMessageContent(message_text=query_result.message),
    )
    await query.answer(results=[result], cache_time=0)
