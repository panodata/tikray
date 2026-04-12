import functools
import pydoc
import typing as t

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
        raise ValueError(f"Unknown dtype name: {name}")
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
