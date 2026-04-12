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
import re
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
        """
        Resolve macro function either from extension or from user-registered function.

        TODO: When using the second (else) code path, this function could make
              the `lf` argument optional after reshuffling logic.
        """
        function = getattr(lf.mp, name, None)  # type: ignore[attr-defined]
        if function is not None:
            # When invoking the extension function in the `lf.mp` namespace,
            # the procedure needs to strip away the first argument.
            return ignoreargs(function, 1)
        else:
            # When invoking a user-registered function,
            # it can be invoked without further ado.
            return self.registry.get(name)

    @staticmethod
    def decode_expression(expression: str) -> t.Tuple[str, t.List[str]]:
        """
        Tokenize the expression and convert it to a tuple describing the macro invocation (function, arg1, arg2, ...).

        TODO: The expression language is currently pretty poor.
              It can certainly be improved in future iterations.
              Any suggestions are very much welcome.
        """

        # Tokenize by colons but read escaped colons literally.
        tokens = re.findall(r"(?:[^:\\]|\\.)+", expression)
        function_name, *args = tokens
        args = [a.replace("\\:", ":") for a in args]

        return function_name, args

    def apply(self, lf: pl.LazyFrame) -> pl.LazyFrame:
        """Convert transformation recipes to Polars expressions and apply to structured pipeline."""

        # Convert all macro expressions to Polars LazyFrame transformations.
        for expression in self.expressions:
            # Decode macro expression into macro invocation descriptor.
            function_name, function_args = self.decode_expression(expression)

            # Resolve UDF from MacroPipe built-ins or user-registered functions.
            function = self.resolve_function(function_name, lf)

            # Add transformation to pipeline.
            lf = lf.pipe(function, *function_args)

        return lf
