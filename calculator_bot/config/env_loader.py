import typing as tp
from os import environ

IS_SETTING_DEFAULT_DISABLED = "__INTERNAL_DEFAULT_DISABLED__"


def load_setting(
        var_name: str,
        type_fn: tp.Callable[[tp.Any], tp.Any] = lambda x: x,
        default: tp.Any = IS_SETTING_DEFAULT_DISABLED
) -> tp.Any:
    try:
        if default == IS_SETTING_DEFAULT_DISABLED:
            value = environ[var_name]
        else:
            value = environ.get(var_name, default)

        if default is None and value == default:
            return value
        return type_fn(value)
    except Exception as exc:
        print(f"Failed to load setting '{var_name}' ({type_fn.__name__}) from env : {exc.__class__.__name__} - {exc}")
        raise
