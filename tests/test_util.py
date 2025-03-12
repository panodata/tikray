from pathlib import Path

import jmespath
import jq
import jsonpointer
import orjsonl
import pytest
import transon
from tikray.util.data import load_json, save_json
from tikray.util.expression import compile_expression
from tikray.util.locator import to_pointer


def test_to_pointer_string():
    assert to_pointer("/") == jsonpointer.JsonPointer("/")
    assert to_pointer("") == jsonpointer.JsonPointer("")


def test_to_pointer_jsonpointer():
    assert to_pointer(jsonpointer.JsonPointer("/")) == jsonpointer.JsonPointer("/")


def test_to_pointer_none():
    with pytest.raises(TypeError) as ex:
        to_pointer(None)
    assert ex.match("Value is not of type str or JsonPointer: NoneType")


def test_to_pointer_int():
    with pytest.raises(TypeError) as ex:
        to_pointer(42)
    assert ex.match("Value is not of type str or JsonPointer: int")


def test_compile_expression_jmes():
    transformer: jmespath.parser.ParsedResult = compile_expression(type="jmes", expression="@")
    assert transformer.expression == "@"
    assert transformer.parsed == {"type": "current", "children": []}


def test_compile_expression_jq():
    transformer: jq._Program = compile_expression(type="jq", expression=".")
    assert transformer.program_string.endswith(".")


def test_compile_expression_transon():
    transformer: transon.Transformer = compile_expression(type="transon", expression={"$": "this"})
    assert transformer.template == {"$": "this"}


def test_compile_expression_unknown():
    with pytest.raises(TypeError) as ex:
        compile_expression(type="foobar", expression=None)
    assert ex.match("Compilation failed. Type must be either jmes or jq or transon: foobar")


def test_load_jsonl_by_suffix(tmp_path: Path):
    data = load_json(Path("examples/eai-warehouse.json"))
    tmp_path = tmp_path / "testdrive.jsonl"
    orjsonl.save(tmp_path, [data])
    assert load_json(tmp_path) == [data]


def test_load_jsonl_by_flag(tmp_path: Path):
    data = load_json(Path("examples/eai-warehouse.json"))
    tmp_path = tmp_path / "testdrive.json"
    save_json([data], tmp_path, use_jsonl=True)
    assert load_json(tmp_path, use_jsonl=True) == [data]
