import typing as t

import orjson
import rsonpy


class RsonTransformer:
    """
    A wrapper around rsonpath, a blazing fast, SIMD-powered JSONPath query engine written in Rust.

    - https://github.com/rsonquery/rsonpath
    - https://github.com/rsonquery/rsonpy

    This is a little wrapper to make rsonpy transformations fit the processing
    style/interface of the other transformation modules, which is mostly list-first.

    That also matches usual applications like processing JSONL/NDJSON data, which
    are streaming multiple records instead of just crunching single documents.

    Here, because rson currently just offers an interface that accepts
    `object`-type root documents, the wrapper needs to conduct a few
    workarounds that obviously include too many code smells to make it
    into a bearable implementation, see below.

    However, the wrapper currently satisfies a few basic test
    cases of the test suite (idempotency and simple slicing),
    mirroring the corresponding jqlang-based test cases,
    so, thanks for all the fish.

    -- https://www.youtube.com/watch?v=aB_9bP21Xxs
    -- https://www.youtube.com/watch?v=waq6EfRhoqg
    """

    def __init__(self, expression: str, **kwargs):
        self.expression = expression

    def transform(self, data: t.Any):
        """
        Apply rson transformation, with workaround for lists as input data.
        """
        expression = self.expression

        if isinstance(data, dict):
            return self.rson_transform(data, self.expression)

        # Wrap the input data into a root document, and adjust the expression correspondingly.
        data = {"__root__": data}
        if expression.startswith("$."):
            expression = "$.__root__." + expression[2:]

        # Apply transformation.
        payload = self.rson_transform(data, expression)

        # If the root document wrapper comes through, for example
        # on the idempotency operation, remove it again.
        if "__root__" in payload:
            return payload["__root__"]

        return payload

    @staticmethod
    def rson_transform(data: t.Any, expression: str) -> t.Any:
        """
        Invoke the rsonpy module for conducting the transformation.

        FIXME: Because rsonpy currently only provides a string-based interface,
               the code needs to nest a few encoders and decoders.
               When possible, provide a better interface like the other
               modules are doing it? The `jqlang` interface can be used
               as a blueprint.

        TODO: Because the transformation returns a generator, the code is currently
              evaluating it, just using `next`, effectively expecting a single item
              to be produced.
              Of course, this might be a performance and memory hog if the generator
              produces multiple items, but c'est la vie for the time being.
              In any case, evaluate if the procedure is sound, or if using `list()`
              would be correct to produce multiple items wrapped into a sequence.
              In this case however, it would be difficult to receive single scalar
              values from a transformation, which is currently possible.
        """
        return next(rsonpy.loads(orjson.dumps(data).decode(), expression, json_loader=orjson.loads))
