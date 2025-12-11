from typing import Any

import orjson
import rsonpy


class RsonTransformer:
    """
    A wrapper around rsonpath, a blazing fast, SIMD-powered JSONPath query engine written in Rust.

    - https://github.com/rsonquery/rsonpath
    - https://github.com/rsonquery/rsonpy
    - https://www.rfc-editor.org/rfc/rfc9535.html

    > Rsonpath is made to filter document ahead of parsing/loading. Think of it more like a way to
    > select a small part of the documents before loading it into memory. It will shine in situations
    > where you have a JSON file too big to hold in memory but you nevertheless want to load parts of it.

    > Rsonpath does not load anything into memory.
    > It only works on the raw JSON, not on an in-memory data structure.

    The wrapper currently satisfies a few basic test cases of the test suite
    in `test_moksha.py` (idempotency, simple slicing, and unwrapping),
    mirroring the corresponding jqlang-based test cases.

    Rsonpath can't do much more by design: It is not suitable to perform advanced
    restructuring, because JSONPath just can't do that.
    """

    def __init__(self, expression: str, **kwargs):  # kwargs for API consistency with other transformers
        self.expression = expression

    def transform(self, data: Any) -> Any:
        """
        Apply transformation with rsonpath by invoking the rsonpy module, using the `orjson` JSON serializer.

        Because rsonpy only provides a string-based interface,
        the code needs to nest a few encoders and decoders.
        """
        return next(rsonpy.loads(orjson.dumps(data).decode(), self.expression, json_loader=orjson.loads), None)
