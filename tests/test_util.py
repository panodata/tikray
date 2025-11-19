from pathlib import Path

import jmespath
import jq
import jsonpointer
import orjsonl
import pytest
import transon

from tikray.util.data import load_json, save_json, to_list
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
    assert ex.match("Compilation failed. Type must be one of .+: foobar")


@pytest.mark.parametrize("input_", ["examples/acme/conversation.json", "examples/eai-warehouse.json"])
def test_load_jsonl_by_suffix(tmp_path: Path, input_: str):
    # Prepare.
    data = load_json(Path(input_))
    tmp_path = tmp_path / "testdrive.jsonl"
    orjsonl.save(tmp_path, to_list(data))

    # Validate.
    assert list(load_json(tmp_path)) == to_list(data)


@pytest.mark.parametrize("input_", ["examples/acme/conversation.json", "examples/eai-warehouse.json"])
def test_load_jsonl_by_flag(tmp_path: Path, input_: str):
    # Prepare.
    data = load_json(Path(input_))
    tmp_path = tmp_path / "testdrive.json"
    save_json(to_list(data), tmp_path, use_jsonl=True)

    # Validate.
    assert list(load_json(tmp_path, use_jsonl=True)) == to_list(data)


def test_to_list():
    assert to_list(None) is None
    assert to_list("foobar") == ["foobar"]
