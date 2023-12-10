from asyncio import sleep

from calculator_bot.libs.calculator import errors
from calculator_bot.libs.calculator.const import (CALC_DIGIT_SYMBOLS,
                                                  CalcActions)
from calculator_bot.libs.calculator.models import (CalcQueryAction,
                                                   CalcQueryDigit)


class Calculator:
    def __init__(self, parentheses_limit: int = 0) -> None:
        self.query = self.query_origin = None
        self.parentheses_limit = parentheses_limit

    async def solve(self, query: str) -> float:
        self.query_origin = query
        self.query = self._sanitize(query)
        self._validate_query(self.query)

        await self.solve_groups()
        return float(self.query)

    async def solve_groups(self, start: int | None = None) -> int | None:
        query_start = cursor = start or 0
        query_len = len(self.query)
        await sleep(0)
        while cursor < query_len:

            if self.query[cursor] == "(":
                cursor = await self.solve_groups(cursor + 1)
                query_len = len(self.query)
                continue

            if self.query[cursor] == ")":
                group_result = str(
                    await self.solve_group(self.query[query_start:cursor])
                )
                self.query = (
                    self.query[: query_start - 1]
                    + group_result
                    + self.query[cursor + 1:]
                )
                return query_start + len(group_result) - 1

            cursor += 1

        self.query = (
                self.query[: query_start]
                + str(await self.solve_group(self.query[query_start:cursor]))
                + self.query[cursor:]
        )
        return cursor

    async def solve_group(self, query: str) -> CalcQueryDigit:  # pylint: disable=R0912  # noqa: C901
        digits = []
        actions = []
        action = digit = ""
        element_start = None
        query_len = len(query)

        await sleep(0)
        for idx in range(query_len):
            current_element = query[idx]
            next_element = "" if idx == query_len - 1 else query[idx + 1]
            if not any((digit, action)):
                element_start = idx

            if self.is_action(current_element):
                if (idx == 0 or action) and current_element == "-" and next_element.isdigit():

                    if action:
                        complete_action = self.store_action(
                            action, next_element, element_start, idx - 1
                        )
                        if complete_action:
                            actions.append(complete_action)
                            action = ""

                    element_start = idx
                    digit += current_element
                else:
                    action += current_element

            elif self.is_digit(current_element):
                if all((current_element == '.', '.' in digit)):
                    raise errors.UnknownQueryElementError("Number cannot contain more than one point")
                digit += current_element

            else:
                raise errors.UnknownQueryElementError(f"Cannot parse symbol '{current_element}' at position {idx}")

            if action:
                complete_action = self.store_action(action, next_element, element_start, idx)
                if complete_action:
                    actions.append(complete_action)
                    action = ""

            elif digit and not self.is_digit(next_element):
                digits.append(CalcQueryDigit(digit, element_start, idx))
                digit = ""

        if len(actions) != len(digits) - 1:
            raise errors.IncorrectQueryError(
                f"Incorrect amount of digits and actions. Actions: {len(actions)}, digits: {len(digits)}"
            )

        return await self.solve_group_query(digits, actions)

    @classmethod
    async def solve_group_query(cls, digits: list[CalcQueryDigit], actions: list[CalcQueryAction]) -> CalcQueryDigit:
        for action in sorted(actions, reverse=True):
            used_digits = []
            used_digits_num = 0

            for idx, digit in enumerate(digits):
                if any((digit.end + 1 == action.start, digit.start - 1 == action.end)):
                    used_digits.append(idx)
                    used_digits_num += 1

                if used_digits_num == 2:
                    break

            result = cls.solve_single_query([digits[x] for x in used_digits], action)
            digits[used_digits[0]] = result
            digits.pop(used_digits[-1])

            # This is a workaround for asyncio.sleep(0) to allow other tasks to run
            await sleep(0)

        return digits[0]

    @staticmethod
    def solve_single_query(digits: list[CalcQueryDigit], action: CalcQueryAction) -> CalcQueryDigit:
        return CalcQueryDigit(action.callback(*digits), start=digits[0].start, end=digits[-1].end)

    @classmethod
    def store_action(cls, element, next_element, start, end) -> CalcQueryAction | None:
        if not cls.is_action(next_element):
            try:
                return CalcQueryAction(element, start, end, CalcActions.PRIORITY_MAPPING.value[element])
            except KeyError:
                raise errors.UnknownQueryElementError(f"Unknown action symbol: {element}")

        return None

    @staticmethod
    def is_action(value: str) -> bool:
        if value in CalcActions.SYMBOLS_LIST.value:
            return True
        return False

    @staticmethod
    def is_digit(value: str | None) -> bool:
        if value in CALC_DIGIT_SYMBOLS:
            return True
        return False

    @staticmethod
    def _sanitize(query: str) -> str:
        return query.replace(",", ".").replace(" ", "").replace("**", "^")

    def _validate_query(self, query: str) -> None:
        open_parentheses = close_parentheses = 0
        for symbol in query:
            if symbol == "(":
                open_parentheses += 1
                if self.parentheses_limit and open_parentheses > self.parentheses_limit:
                    raise errors.IncorrectQueryError(
                        f"Max amount of parentheses exceeded: {self.parentheses_limit}"
                    )
            elif symbol == ")":
                close_parentheses += 1

        if open_parentheses != close_parentheses:
            raise errors.IncorrectQueryError(
                "Amount of open parentheses doesn't match closing ones"
            )
