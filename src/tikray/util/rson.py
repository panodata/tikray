import typing as t

import orjson
import rsonpy


class RsonTransformer:
    """
    A wrapper around rsonpath, a blazing fast, SIMD-powered JSONPath query engine written in Rust.

    - https://github.com/rsonquery/rsonpath
    - https://github.com/rsonquery/rsonpy

    The wrapper currently satisfies just a few basic test cases of the test suite
    in `test_moksha.py` (idempotency and simple slicing), mirroring the corresponding
    jqlang-based test cases.
    """

    def __init__(self, expression: str, **kwargs):
        self.expression = expression

    def transform(self, data: t.Any):
        """
        Apply rson transformation.
        """
        return self.rson_transform(data, self.expression)

    @staticmethod
    def rson_transform(data: t.Any, expression: str) -> t.Any:
        """
        Invoke the rsonpy module for conducting the transformation, using the `orjson` JSON serializer.

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
              In this case however, it might be difficult to receive single scalar
              values from a transformation, which is currently possible.
        """
        try:
            return next(rsonpy.loads(orjson.dumps(data).decode(), expression, json_loader=orjson.loads))
        except StopIteration:
            return None
