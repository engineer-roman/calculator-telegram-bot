from loguru import logger as log
from dataclasses import dataclass

from sentry_sdk import capture_exception

from calculator_bot.libs.calculator import Calculator, IncorrectQueryError
from calculator_bot.libs.calculator.errors import UnknownQueryElementError


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

    """Class to process queries"""
    async def process(self, query: str) -> QueryResult:
        if not query:
            result_str = "Waiting for query"
            message = "Empty query provided"
            error = False

        else:
            try:
                result_str, message, error = await self._process_query(query)
            except Exception as exc:
                log.exception("Failed to process query", exc_info=exc)
                capture_exception(exc)
                result_str = "Result: Error occurred :("
                message = f"An error occurred while processing the query"
                error = True

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

        except (IncorrectQueryError, UnknownQueryElementError):
            result_str = "Result: Incorrect query"
            message = f"Incorrect query: {query}"
            error = True

        return result_str, message, error
