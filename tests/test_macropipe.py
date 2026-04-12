import re
from io import StringIO

import polars as pl
import pytest
from polars.testing import assert_frame_equal

from tikray.macropipe import MacroPipe, recipe
from tikray.macropipe.util import decode_list, gettype


def test_util_gettype():
    """Validate the `gettype` utility function."""
    assert gettype("str") is str
    assert gettype("float") is float
    with pytest.raises(ValueError) as excinfo:
        gettype("Hotzenplotz")
    assert excinfo.match("Unknown dtype name: Hotzenplotz")


def test_util_decode_list():
    """Validate the `decode_list` utility function."""
    assert decode_list("a,b") == ["a", "b"]
    assert decode_list(["a", "b"]) == ["a", "b"]


def test_core_decode_expression_success():
    """Validate the `decode_expression` core method."""
    assert MacroPipe.decode_expression("foo") == ("foo", [])
    assert MacroPipe.decode_expression("foo:bar") == ("foo", ["bar"])


def test_core_decode_expression_errors():
    """
    Validate error cases of the `decode_expression` core method.

    Avoid uncaught unpacking errors when expression is empty or delimiter-only.
    """

    # Empty expression.
    with pytest.raises(ValueError) as excinfo:
        MacroPipe.decode_expression(None)
    assert excinfo.match("Invalid MacroPipe expression: None")

    with pytest.raises(ValueError) as excinfo:
        MacroPipe.decode_expression("")
    assert excinfo.match("Invalid MacroPipe expression: ")

    # Delimiter-only expression.
    with pytest.raises(ValueError) as excinfo:
        MacroPipe.decode_expression(":::")
    assert excinfo.match("Invalid MacroPipe expression: ':::'")

    # Dangling trailing escapes.
    with pytest.raises(ValueError) as excinfo:
        MacroPipe.decode_expression("concat:a:\\")
    assert excinfo.match(re.escape(r"Invalid MacroPipe expression: 'concat:a:\\'"))


def test_head():
    """Validate the `head` function."""
    input_frame = pl.LazyFrame({"value": [42.42, 84.84]})
    output_frame = pl.LazyFrame({"value": [42.42]})
    pipe = MacroPipe.from_recipes(
        "head:1",
    )
    converted_frame = input_frame.mp.apply(pipe)
    assert_frame_equal(converted_frame, output_frame)


def test_tail():
    """Validate the `tail` function."""
    input_frame = pl.LazyFrame({"value": [42.42, 84.84]})
    output_frame = pl.LazyFrame({"value": [84.84]})
    pipe = MacroPipe.from_recipes(
        "tail:1",
    )
    converted_frame = input_frame.mp.apply(pipe)
    assert_frame_equal(converted_frame, output_frame)


def test_first():
    """Validate the `first` function."""
    input_frame = pl.LazyFrame({"value": [42.42, 84.84]})
    output_frame = pl.LazyFrame({"value": [42.42]})
    pipe = MacroPipe.from_recipes(
        "first",
    )
    converted_frame = input_frame.mp.apply(pipe)
    assert_frame_equal(converted_frame, output_frame)


def test_last():
    """Validate the `last` function."""
    input_frame = pl.LazyFrame({"value": [42.42, 84.84]})
    output_frame = pl.LazyFrame({"value": [84.84]})
    pipe = MacroPipe.from_recipes(
        "last",
    )
    converted_frame = input_frame.mp.apply(pipe)
    assert_frame_equal(converted_frame, output_frame)


def test_format_standard():
    """
    Validate the `format` function.

    https://docs.pola.rs/api/python/stable/reference/expressions/api/polars.format.html
    """
    input_frame = pl.LazyFrame({"a": ["a", "b", "c"], "b": [1, 2, 3]})
    output_frame = pl.LazyFrame({"value": ["foo_a_bar_1", "foo_b_bar_2", "foo_c_bar_3"]})
    pipe = MacroPipe.from_recipes(
        "format:foo_{}_bar_{}:a,b:value:drop=true",
    )
    converted_frame = input_frame.mp.apply(pipe)
    assert_frame_equal(converted_frame, output_frame)


def test_format_including_colon():
    """
    Validate the `format` function, including escaped colons.

    This is special, because the current miniature expression language uses colons as
    separators between function name and arguments.
    """
    input_frame = pl.LazyFrame({"a": ["a"], "b": [1]})
    output_frame = pl.LazyFrame({"value": ["foo: a, bar: 1"]})
    pipe = MacroPipe.from_recipes(
        r"format:foo\: {}, bar\: {}:a,b:value:drop=true",
    )
    converted_frame = input_frame.mp.apply(pipe)
    assert_frame_equal(converted_frame, output_frame)


def test_filter():
    """
    Validate the `filter` function.
    """

    csv = """
timestamp,data
1754784000000,foo
1754785000000,bar
        """.strip()
    input_frame = pl.scan_csv(StringIO(csv))
    output_frame = pl.LazyFrame({"timestamp": [1754784000000], "data": ["foo"]})
    pipe = MacroPipe.from_recipes(
        "filter:timestamp < 1754785000000",
    )
    converted_frame = input_frame.mp.apply(pipe)
    assert_frame_equal(converted_frame.collect(), output_frame.collect())


def test_apply_macropipe():
    """Validate MacroPipe's `apply` function."""
    input_frame = pl.LazyFrame({"value": [42.42]})
    output_frame = pl.LazyFrame({"value": ["42.42"]})
    pipe = MacroPipe.from_recipes(
        "cast:value:str",
    )
    # Invoke `apply` on the `MacroPipe` instance.
    converted_frame = pipe.apply(input_frame)
    assert_frame_equal(converted_frame, output_frame)


def test_apply_extension():
    """Validate the extension's `apply` function."""
    input_frame = pl.LazyFrame({"value": [42.42]})
    output_frame = pl.LazyFrame({"value": ["42.42"]})
    pipe = MacroPipe.from_recipes(
        "cast:value:str",
    )
    # Invoke `apply` on the `mp` namespace of the `LazyFrame` instance.
    converted_frame = input_frame.mp.apply(pipe)
    assert_frame_equal(converted_frame, output_frame)


def test_user_registered_recipe():
    """
    Validate a user-registered transformation recipe.
    """

    @recipe
    def hello(lf: pl.LazyFrame, column_name: str) -> pl.LazyFrame:
        return lf.with_columns(pl.concat_str(pl.lit("Hello"), pl.col(column_name), separator=" ").alias(column_name))

    input_frame = pl.LazyFrame({"value": [42.42]})
    output_frame = pl.LazyFrame({"value": ["Hello 42.42"]})
    pipe = MacroPipe.from_recipes(
        "hello:value",
    )
    converted_frame = pipe.apply(input_frame)
    assert_frame_equal(converted_frame, output_frame)


def test_cast_scalar_str_macro():
    """
    Validate casting columns to string type, macro style.
    """
    input_frame = pl.LazyFrame({"float": [42.42], "int": [42], "str": ["42"]})
    output_frame = pl.LazyFrame({"float": ["42.42"], "int": ["42"], "str": ["42"]})
    pipe = MacroPipe.from_recipes(
        "cast:float,int,str:str",
    )
    converted_frame = pipe.apply(input_frame)
    assert_frame_equal(converted_frame, output_frame)


def test_cast_scalar_str_extension():
    """
    Validate casting columns to string type, extension style.
    """
    input_frame = pl.LazyFrame({"float": [42.42], "int": [42], "str": ["42"]})
    output_frame = pl.LazyFrame({"float": ["42.42"], "int": ["42"], "str": ["42"]})
    converted_frame = input_frame.mp.cast("float,int,str", "str")
    assert_frame_equal(converted_frame, output_frame)


def test_cast_scalar_float():
    """
    Validate casting columns to float type.
    """
    input_frame = pl.LazyFrame({"float": ["42.42"], "int": ["42"], "str": ["42"]})
    output_frame = pl.LazyFrame({"float": [42.42], "int": [42.0], "str": [42.0]})
    pipe = MacroPipe.from_recipes(
        "cast:float,int,str:float",
    )
    converted_frame = pipe.apply(input_frame)
    assert_frame_equal(converted_frame, output_frame)


def test_select_columns():
    """
    Validate selecting columns.
    """
    csv = """
timestamp,data,garbage1,garbage2
1754784000000,foo,bar,baz
    """.strip()
    input_frame = pl.scan_csv(StringIO(csv))
    output_frame = pl.LazyFrame({"timestamp": [1754784000000], "data": ["foo"]})
    pipe = MacroPipe.from_recipes(
        "select:timestamp,data",
    )
    converted_frame = input_frame.mp.apply(pipe)
    assert_frame_equal(converted_frame, output_frame)


def test_drop_columns():
    """
    Validate dropping columns.
    """
    csv = """
timestamp,data,garbage1,garbage2
1754784000000,foo,bar,baz
    """.strip()
    input_frame = pl.scan_csv(StringIO(csv))
    output_frame = pl.LazyFrame({"timestamp": [1754784000000], "data": ["foo"]})
    pipe = MacroPipe.from_recipes(
        "drop:garbage1,garbage2",
    )
    converted_frame = pipe.apply(input_frame)
    assert_frame_equal(converted_frame, output_frame)


def test_rename_column():
    """
    Validate renaming a column.
    """
    csv = """
_id,data
42,Hotzenplotz
    """.strip()
    input_frame = pl.scan_csv(StringIO(csv))
    output_frame = pl.LazyFrame({"__id": [42], "data": ["Hotzenplotz"]})
    pipe = MacroPipe.from_recipes(
        "rename:_id:__id",
    )
    converted_frame = pipe.apply(input_frame)
    assert_frame_equal(converted_frame, output_frame)


def test_concat_comma():
    """
    Validate combining columns.
    """
    input_frame = pl.LazyFrame({"float": [42.42], "int": [42], "str": ["42"]})
    output_frame = pl.LazyFrame({"combined": ["42.42,42,42"]})
    pipe = MacroPipe.from_recipes(
        "concat:float,int,str:,:combined:drop=true",
    )
    converted_frame = pipe.apply(input_frame)
    assert_frame_equal(converted_frame, output_frame)


def test_concat_space():
    """
    Validate combining columns, where the separator is a space.
    """
    input_frame = pl.LazyFrame({"firstname": ["Räuber"], "lastname": ["Hotzenplotz"]})
    output_frame = pl.LazyFrame({"name": ["Räuber Hotzenplotz"]})
    pipe = MacroPipe.from_recipes(
        "concat:firstname,lastname: :name:drop=true",
    )
    converted_frame = pipe.apply(input_frame)
    assert_frame_equal(converted_frame, output_frame)


def test_scale():
    """
    Validate scaling values.
    """
    input_frame = pl.LazyFrame({"value": [4242]})
    output_frame = pl.LazyFrame({"value": [42.42]})
    pipe = MacroPipe.from_recipes(
        "scale:value:0.01",
    )
    converted_frame = pipe.apply(input_frame)
    assert_frame_equal(converted_frame, output_frame)


def test_iso_to_unixtime():
    """
    Validate converting ISO-8601 format to epoch timestamp (Unix time).
    """
    input_frame = pl.LazyFrame({"value": ["2026-03-03T12:12:12"]})
    output_frame = pl.LazyFrame({"value": [1772539932]})
    pipe = MacroPipe.from_recipes(
        "iso_to_unixtime:value",
    )
    converted_frame = pipe.apply(input_frame)
    assert_frame_equal(converted_frame, output_frame)


def test_unixtime_to_iso():
    """
    Validate converting epoch timestamp (Unix time) to ISO-8601 format.
    """
    input_frame = pl.LazyFrame({"value": [1772539932]})
    output_frame = pl.LazyFrame({"value": ["2026-03-03T12:12:12.000000"]})
    pipe = MacroPipe.from_recipes(
        "unixtime_to_iso:value",
    )
    converted_frame = pipe.apply(input_frame)
    assert_frame_equal(converted_frame, output_frame)


def test_earth_observations_coords_python():
    """
    Validate decoding a CSV file with special features for importing into CrateDB.

    The procedure applies two transformations before the data is ready for importing into
    CrateDB.

    - Convert coordinates in JSON list format to WKT POINT format.
    - Convert a dictionary encoded in proprietary Python format into standard JSON format.

    https://gist.github.com/amotl/949547787e116c8cafabe2959281e7ec
    """
    pytest.importorskip("polars_st")
    csv = """
timestamp,coords,data
1754784000000,"[9.757, 47.389]","{'temperature': 42.42}"
    """.strip()
    input_frame = pl.scan_csv(StringIO(csv), quote_char='"')
    output_frame = pl.LazyFrame(
        {"timestamp": [1754784000000], "coords": ["POINT (9.757 47.389)"], "data": ['{"temperature":42.42}']}
    )
    pipe = MacroPipe.from_recipes(
        "json_array_to_wkt_point:coords",
        "python_to_json:data",
    )
    converted_frame = pipe.apply(input_frame)
    assert_frame_equal(converted_frame, output_frame)


def test_combine_coords_cells():
    """
    Validate combining two columns into one.
    """
    pytest.importorskip("polars_st")
    csv = """
timestamp,longitude,latitude
1754784000000,9.757,47.389
    """.strip()
    input_frame = pl.scan_csv(StringIO(csv))
    output_frame = pl.LazyFrame({"timestamp": [1754784000000], "coords": ["POINT (9.757 47.389)"]})
    pipe = MacroPipe.from_recipes(
        "columns_to_json_array:longitude,latitude:coords:drop=true",
        "json_array_to_wkt_point:coords",
    )
    converted_frame = pipe.apply(input_frame)
    assert_frame_equal(converted_frame, output_frame)


def test_extract_json_columns():
    """
    Validate extracting fields from JSON into columns.
    """
    csv = """
timestamp,data
1754784000000,'{"longitude": 9.757, "latitude": 47.389}'
    """.strip()
    input_frame = pl.scan_csv(StringIO(csv), quote_char="'")
    pipe = MacroPipe.from_recipes(
        "json_fields_to_columns:data:longitude,latitude:float:drop=true",
    )
    output_frame = pl.LazyFrame({"timestamp": [1754784000000], "longitude": [9.757], "latitude": [47.389]})
    converted_frame = pipe.apply(input_frame)
    assert_frame_equal(converted_frame, output_frame)


def test_extract_json_coords():
    """
    Validate extracting fields from JSON into WKT POINT.
    """
    pytest.importorskip("polars_st")
    csv = """
timestamp,data
1754784000000,"{""lon"": 9.757, ""lat"": 47.389}"
    """.strip()
    input_frame = pl.scan_csv(StringIO(csv))
    output_frame = pl.LazyFrame({"timestamp": [1754784000000], "coords": ["POINT (9.757 47.389)"]})
    pipe = MacroPipe.from_recipes(
        "json_fields_to_wkt_point:data:lon:lat:coords:drop=true",
    )
    converted_frame = pipe.apply(input_frame)
    assert_frame_equal(converted_frame, output_frame)
