import operator
from enum import Enum

CALC_DIGIT_SYMBOLS = {str(x) for x in range(10)}.union(".")


class CalcActions(Enum):
    SUMMARIZE = "+"
    DIFFERENCE = "-"
    MULTIPLY = "*"
    DIVISION = "/"
    FLOOR_DIVISION = "//"
    EXPONENT = "^"
    CALLBACK_MAPPING = {
        SUMMARIZE: operator.add,
        DIFFERENCE: operator.sub,
        MULTIPLY: operator.mul,
        DIVISION: operator.truediv,
        FLOOR_DIVISION: operator.floordiv,
        EXPONENT: operator.pow,
    }
    PRIORITY_MAPPING = {
        SUMMARIZE: 1,
        DIFFERENCE: 1,
        MULTIPLY: 2,
        DIVISION: 2,
        FLOOR_DIVISION: 2,
        EXPONENT: 3,
    }
    SYMBOLS_LIST = (
        SUMMARIZE,
        DIFFERENCE,
        MULTIPLY,
        DIVISION,
        EXPONENT
    )
