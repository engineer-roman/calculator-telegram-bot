from dataclasses import dataclass

from loguru import logger as log
from prometheus_client import Counter, Summary
from sentry_sdk import capture_exception

from calculator_bot.libs.calculator import Calculator, IncorrectQueryError
from calculator_bot.libs.calculator.errors import UnknownQueryElementError

QUERY_PROCESS_SEC_METRIC = Summary("calc_query_process_seconds", "Time spent calculating query")
QUERY_COUNT_METRIC = Counter("calc_query", "Number of queries processed", ["error"])


@dataclass
class QueryResult:
    """Class to hold the results of a query."""
    query: str
    result: str
    message: str
    error: bool


class QueryProcessor:
    def __init__(self, parentheses_limit: int) -> None:
        self._parentheses_limit = parentheses_limit

    @QUERY_PROCESS_SEC_METRIC.time()
    async def process(self, query: str) -> QueryResult:
        if not query:
            result_str = "Waiting for query"
            message = "Empty query provided"
            error = False

        else:
            try:
                result_str, message, error = await self._process_query(query)
            except Exception as exc:  # pylint: disable=W0703
                log.exception("Failed to process query", exc_info=exc)
                capture_exception(exc)
                result_str = "Result: Error occurred :("
                message = "An error occurred while processing the query"
                error = True

        QUERY_COUNT_METRIC.labels(error=error).inc()
        return QueryResult(
            query=query,
            result=result_str,
            message=message,
            error=error
        )

    async def _process_query(self, query: str) -> tuple[str, str, bool]:
        try:
            result = await Calculator(self._parentheses_limit).solve(query)
            result_str = str(result)

            if result_str.endswith(".0"):
                result_str = result_str[:-2]
            message = f"{query} = {result_str}"
            error = False

        except (IncorrectQueryError, UnknownQueryElementError) as exc:
            log.error(f"Failed to process query '{query}': {exc.__class__.__name__} - {exc}")
            result_str = "Result: Incorrect query"
            message = f"Incorrect query: {query}"
            error = True

        return result_str, message, error
