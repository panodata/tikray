"""
A small macro language on top of Polars.

This pipeline wrapper uses macro-like commands / a textual expression language,
that uses Polars pipes to apply compiled UDFs to a LazyFrame in a structured way.

https://tikray.readthedocs.io/engine/polars/
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
    registry: t.ClassVar[Registry] = Registry()

    @classmethod
    def from_recipes(cls, *recipes: str) -> "MacroPipe":
        """Create MacroPipe from list of recipes (textual macro commands)."""
        return cls(expressions=list(recipes))

    def resolve_function(self, name: str, lf: t.Optional[pl.LazyFrame] = None) -> t.Callable:
        """
        Resolve macro function either from extension or from user-registered function.
        """
        mp_namespace = getattr(lf, "mp", None) if lf is not None else None
        function = getattr(mp_namespace, name, None) if mp_namespace is not None else None
        if callable(function):
            # When invoking the extension function in the `lf.mp` namespace,
            # the procedure needs to strip away the first argument.
            return ignoreargs(function, 1)
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

        if not expression:
            raise ValueError(f"Invalid MacroPipe expression: {expression!r}")

        # Reject dangling trailing escapes before tokenization.
        # A malformed expression ending with an unmatched backslash silently loses
        # data during tokenization (e.g., concat:a:\ tokenizes to ['concat', 'a']
        # with the final \ dropped), which leads to confusing downstream behaviour.
        trailing_backslashes = len(expression) - len(expression.rstrip("\\"))
        if trailing_backslashes % 2:
            raise ValueError(f"Invalid MacroPipe expression: {expression!r}")

        # Tokenize by colons but read escaped colons literally.
        tokens = re.findall(r"(?:[^:\\]|\\.)+", expression)
        if not tokens:
            raise ValueError(f"Invalid MacroPipe expression: {expression!r}")
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
