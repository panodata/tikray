import sys
import typing as t
from pathlib import Path

import orjson
import orjsonl


def no_privates_no_nulls_no_empties(key, value) -> bool:
    """
    A filter for `attr.asdict`, to suppress private attributes.
    """
    is_private = key.name.startswith("_")
    is_null = value is None
    is_empty = value == []
    if is_private or is_null or is_empty:
        return False
    return True


def no_disabled_false(key, value):
    """
    A filter for `attr.asdict`, to suppress `disabled: false` attributes.
    """
    return not (key.name == "disabled" and value is False)


def load_json(path: Path, use_jsonl: bool = False) -> t.Any:
    if path.suffix in [".jsonl", ".ndjson"] or use_jsonl:
        return orjsonl.load(path)
    else:
        return orjson.loads(path.read_text())


def save_json(data: t.Any, path: t.Optional[Path] = None, use_jsonl: bool = False) -> None:
    # Sanity checks.
    if use_jsonl and not path:
        raise NotImplementedError("JSONL not supported on STDOUT yet, please raise an issue")

    # Output JSONL.
    if path and (path.suffix in [".jsonl", ".ndjson"] or use_jsonl):
        orjsonl.save(path, data)

    # Output JSON.
    elif path:
        with open(path, "wb") as stream:
            stream.write(orjson.dumps(data))

    else:
        sys.stdout.buffer.write(orjson.dumps(data))
