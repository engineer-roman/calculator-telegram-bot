class CalcError(Exception):
    ...


class IncorrectQueryError(CalcError):
    ...


class UnknownQueryElementError(CalcError):
    ...
