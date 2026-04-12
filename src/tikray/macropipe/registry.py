import typing as t


class Registry:
    """MacroPipe function registry"""

    r: t.ClassVar[t.Dict[str, t.Callable]] = {}

    @classmethod
    def register(cls, fn: t.Callable) -> None:
        """Register a MacroPipe recipe function."""
        if fn.__name__ in cls.r:
            raise ValueError(f"MacroPipe function already registered: {fn.__name__}")
        cls.r[fn.__name__] = fn

    @classmethod
    def get(cls, name: str) -> t.Callable:
        """Get a MacroPipe recipe function by name."""
        if name not in cls.r:
            raise NotImplementedError(f"MacroPipe function not implemented: {name}")
        return cls.r[name]


def recipe(function: t.Callable) -> t.Callable:
    """Decorator to register a MacroPipe recipe function."""
    Registry.register(function)
    return function
