"""
A small macro language on top of Polars.

This pipeline wrapper uses macro-like commands / a textual expression language,
that uses Polars pipes to apply compiled UDFs to a LazyFrame in a structured way.

https://docs.pola.rs/api/python/stable/reference/lazyframe/api/polars.LazyFrame.pipe.html
https://peps.python.org/pep-0638/
https://www.linkedin.com/pulse/dsls-llms-ken-kocienda-fpi1c
https://discuss.python.org/t/functools-pipe-function-composition-utility/69744
"""

import dataclasses
import typing as t

import polars as pl

from tikray.macropipe.registry import Registry
from tikray.macropipe.util import ignoreargs


@dataclasses.dataclass
class MacroPipe:
    """A miniature transformation engine based on Polars."""

    expressions: t.List[str]
    registry: t.ClassVar[Registry] = dataclasses.field(default=Registry())

    @classmethod
    def from_recipes(cls, *recipes: str) -> "MacroPipe":
        """Create MacroPipe from list of recipes (textual macro commands)."""
        return cls(expressions=list(recipes))

    def resolve_function(self, name: str, lf: pl.LazyFrame) -> t.Callable:
        """Resolve macro function either from extension or from user-registered function."""
        function = getattr(lf.mp, name, None)  # type: ignore[attr-defined]
        if function is not None:
            # When invoking the extension function in the `lf.mp` namespace,
            # the procedure needs to strip away the first argument.
            return ignoreargs(function, 1)
        else:
            # When invoking a user-registered function,
            # it can be invoked without further ado.
            return self.registry.get(name)

    def apply(self, lf: pl.LazyFrame) -> pl.LazyFrame:
        """Convert transformation recipes to Polars expressions and apply to structured pipeline."""

        # Convert all expressions.
        for expression in self.expressions:
            # TODO: The expression language is currently pretty poor.
            #       It can certainly be improved in future iterations.
            #       Any suggestions are very much welcome.
            function_name, *args = expression.split(":")

            # Resolve UDF from builtins or registered functions.
            function = self.resolve_function(function_name, lf)

            # Add to pipeline.
            lf = lf.pipe(function, *args)

        return lf
