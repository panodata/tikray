import functools
import pydoc
import typing as t

from polars._typing import PythonDataType


def decode_list(data: t.Union[str, t.List[str]]) -> t.List[str]:
    """Decode comma-separated strings to a list of strings."""
    if isinstance(data, str):
        return list(map(str.strip, data.split(",")))
    return data


def gettype(name: str) -> PythonDataType:
    """
    Lexical cast from string to type.
    https://stackoverflow.com/a/29831586
    """
    return t.cast(PythonDataType, pydoc.locate(name))


def ignoreargs(func, count):
    """
    Decorator that removes a certain number of arguments from the call.
    https://stackoverflow.com/a/32922362
    """

    @functools.wraps(func)
    def fun(*args, **kwargs):
        return func(*(args[count:]), **kwargs)

    return fun
