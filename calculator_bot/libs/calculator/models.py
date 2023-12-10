from calculator_bot.libs.calculator.const import CalcActions


class CalcQueryAction(str):
    def __new__(cls, value, start, end, priority):
        cls = str.__new__(CalcQueryAction, value)
        cls.start = start
        cls.end = end
        cls.priority = priority
        cls.callback = CalcActions.CALLBACK_MAPPING.value[value]
        return cls

    def __lt__(self, value: "CalcQueryAction") -> bool:
        return self.priority < value.priority

    def __gt__(self, value: "CalcQueryAction") -> bool:
        return self.priority > value.priority

    def __eq__(self, value: "CalcQueryAction") -> bool:
        return self.priority == value.priority


class CalcQueryDigit(float):
    def __new__(cls, value, start, end):
        super(CalcQueryDigit, cls).__new__(cls, value)
        cls = float.__new__(CalcQueryDigit, value)
        cls.start = start
        cls.end = end
        return cls
