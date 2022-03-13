from calculator_telegram_bot.calculator import Calculator
from calculator_telegram_bot.errors import IncorrectQuery, UnknownQueryElement
from calculator_telegram_bot.models import InlineQueryResultArticle, InputTextMessageContent
from time import time
from logging import getLogger

log = getLogger("handlers")


async def message_handler(bot, update):
    query = update.data["message"]["text"]
    try:
        log.info(
            f"Incoming text query in update {update.update_id} "
            f"(len: {len(query)}) "
            f"from '{update.data['message']['from'].get('username', '')}' "
            f"<{update.data['message']['from']['id']}>"
        )
        time_start = time()
        result = await Calculator().solve(query)
        log.info(
            f"Query from update {update.update_id} is solved in "
            f"{time() - time_start} sec"
        )
        message = f"{query} = {result}"
    except (IncorrectQuery, UnknownQueryElement):
        log.info(f"Query from update {update.update_id} is incorrect")
        message = f"Incorrect query: {query}"
    except Exception as exc:
        # FIXME send error to Sentry
        log.exception(
            f"Failed to process query in update {update.update_id}"
        )
        return

    await bot.send_message(update.data["message"]["from"]["id"], text=message)


async def inline_handler(bot, update):
    query_id = update.data["inline_query"]["id"]
    query = update.data["inline_query"]["query"]
    if not query:
        return
    try:
        log.info(
            f"Incoming inline query id {query_id} (len: {len(query)})"
            f"from '{update.data['inline_query']['from'].get('username', '')}' "
            f"<{update.data['inline_query']['from']['id']}>"
        )
        time_start = time()
        result = await Calculator().solve(query)
        log.info(f"Query id {query_id} is solved in {time() - time_start} sec")
        message = f"{query} = {result}"
    except (IncorrectQuery, UnknownQueryElement):
        log.info(f"Query id {query_id} is incorrect")
        result = "Incorrect query"
        message = f"Incorrect query: {query}"
    except Exception as exc:
        # FIXME send error to Sentry
        log.exception(
            f"Failed to process query id {query_id} in update {update.update_id}"
        )
        return
    await bot.answer_inline_query(
        inline_query_id=query_id,
        cache_time=0,
        results=[
            InlineQueryResultArticle(
                query_id=query_id,
                title=f"Result: {result}",
                input_message_content=InputTextMessageContent(message)
            ).values()
        ]
    )
