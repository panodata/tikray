import typing as t


class Registry:
    """Function registry for MacroPipe."""

    r: t.Dict[str, t.Callable] = {}

    @classmethod
    def register(cls, fn: t.Callable) -> None:
        cls.r[fn.__name__] = fn

    def get(self, name):
        if name not in self.r:
            raise NotImplementedError(f"MacroPipe function not implemented: {name}")
        return self.r[name]


def recipe(function: t.Callable) -> t.Callable:
    """Decorator to register a MacroPipe recipe function."""
    Registry.register(function)
    return function
