import dataclasses
import typing as t

import polars as pl


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


@dataclasses.dataclass
class MacroPipe:
    """A miniature transformation engine based on Polars."""

    expressions: t.List[str]
    registry: t.ClassVar[Registry] = dataclasses.field(default=Registry())

    @classmethod
    def from_recipes(cls, *recipes: str) -> "MacroPipe":
        """Create MacroPipe from list of recipes (textual macro commands)."""
        return cls(expressions=list(recipes))

    def apply(self, lf: pl.LazyFrame) -> pl.LazyFrame:
        """Convert recipes to Polars expressions and apply as transformation elements."""
        for expression in self.expressions:
            function_name, *args = expression.split(":")
            function = self.registry.get(function_name)
            lf = lf.pipe(function, *args)
        return lf
