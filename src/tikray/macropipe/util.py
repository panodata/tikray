import functools
import pydoc
import typing as t
from ast import literal_eval

import orjson

if t.TYPE_CHECKING:  # pragma: no cover
    PythonDataType: t.TypeAlias = type  # type: ignore[name-defined]


def decode_list(data: t.Union[str, t.List[str]]) -> t.List[str]:
    """Decode comma-separated strings to a list of strings."""
    if isinstance(data, str):
        return list(map(str.strip, data.split(",")))
    return data


def gettype(name: str) -> "PythonDataType":
    """
    Lexical cast from string to type.
    https://stackoverflow.com/a/29831586

    TODO: Please verify if `pydoc.locate()` is a safe call
          and/or investigate if a better solution exists.
    """
    resolved = pydoc.locate(name)
    if resolved is None:
        raise ValueError(f"Symbol does not exist: {name}")
    if not isinstance(resolved, type):
        raise ValueError(f"Resolved symbol is not a Python type: {name}")
    return t.cast("PythonDataType", resolved)


def ignoreargs(func, count):
    """
    Decorator that removes a certain number of arguments from the call.
    https://stackoverflow.com/a/32922362
    """

    @functools.wraps(func)
    def fun(*args, **kwargs):
        return func(*(args[count:]), **kwargs)

    return fun


def to_json(value: t.Optional[str] = None, strict: bool = False) -> t.Optional[str]:
    """
    Convert Python-encoded dictionary into pure JSON.

    Note: The `python_to_json` method uses `ast.literal_eval()` which, while safer
          than `eval()`, still parses arbitrary Python literal expressions from
          input data. Additionally, `map_elements` disables Polars' parallelization.
    """
    if value is None:
        return None

    try:
        return orjson.dumps(literal_eval(value)).decode()
    except (SyntaxError, ValueError, TypeError):
        if strict:
            raise
        return None
