from io import StringIO

import polars as pl
import pytest
from polars.testing import assert_frame_equal

from tikray.macropipe import MacroPipe


def test_cast_scalar_str():
    """
    Validate casting columns to string type.
    """
    input_frame = pl.DataFrame({"float": [42.42], "int": [42], "str": ["42"]})
    output_frame = pl.DataFrame({"float": ["42.42"], "int": ["42"], "str": ["42"]})
    pipe = MacroPipe.from_recipes(
        "cast:float,int,str:str",
    )
    converted_frame = pipe.apply(input_frame.lazy()).collect()
    assert_frame_equal(
        output_frame,
        converted_frame,
    )


def test_cast_scalar_float():
    """
    Validate casting columns to float type.
    """
    input_frame = pl.DataFrame({"float": ["42.42"], "int": ["42"], "str": ["42"]})
    output_frame = pl.DataFrame({"float": [42.42], "int": [42.0], "str": [42.0]})
    pipe = MacroPipe.from_recipes(
        "cast:float,int,str:float",
    )
    converted_frame = pipe.apply(input_frame.lazy()).collect()
    assert_frame_equal(
        output_frame,
        converted_frame,
    )


def test_select_columns():
    """
    Validate selecting columns.
    """
    csv = """
timestamp,data,garbage1,garbage2
1754784000000,foo,bar,baz
    """.strip()
    pipe = MacroPipe.from_recipes(
        "select:timestamp,data",
    )
    df = pl.scan_csv(StringIO(csv))
    df = pipe.apply(df).collect()
    assert_frame_equal(
        df,
        pl.DataFrame({"timestamp": [1754784000000], "data": ["foo"]}),
    )


def test_drop_columns():
    """
    Validate dropping columns.
    """
    csv = """
timestamp,data,garbage1,garbage2
1754784000000,foo,bar,baz
    """.strip()
    pipe = MacroPipe.from_recipes(
        "drop:garbage1,garbage2",
    )
    df = pl.scan_csv(StringIO(csv))
    df = pipe.apply(df).collect()
    assert_frame_equal(
        df,
        pl.DataFrame({"timestamp": [1754784000000], "data": ["foo"]}),
    )


def test_rename_column():
    """
    Validate renaming a column.
    """
    csv = """
_id,data
42,Hotzenplotz
    """.strip()
    pipe = MacroPipe.from_recipes(
        "rename:_id:__id",
    )
    df = pl.scan_csv(StringIO(csv))
    df = pipe.apply(df).collect()
    assert_frame_equal(
        df,
        pl.DataFrame({"__id": [42], "data": ["Hotzenplotz"]}),
    )


def test_concat():
    """
    Validate combining columns.
    """
    input_frame = pl.DataFrame({"float": [42.42], "int": [42], "str": ["42"]})
    output_frame = pl.DataFrame({"combined": ["42.42,42,42"]})
    pipe = MacroPipe.from_recipes(
        "concat:float,int,str:,:combined:drop=true",
    )
    converted_frame = pipe.apply(input_frame.lazy()).collect()
    assert_frame_equal(
        output_frame,
        converted_frame,
    )


def test_scale():
    """
    Validate scaling values.
    """
    input_frame = pl.DataFrame({"value": [4242]})
    output_frame = pl.DataFrame({"value": [42.42]})
    pipe = MacroPipe.from_recipes(
        "scale:value:100",
    )
    converted_frame = pipe.apply(input_frame.lazy()).collect()
    assert_frame_equal(
        output_frame,
        converted_frame,
    )


def test_iso_to_unixtime():
    """
    Validate converting ISO-8601 format to epoch timestamp (Unix time).
    """
    input_frame = pl.DataFrame({"value": ["2026-03-03T12:12:12"]})
    output_frame = pl.DataFrame({"value": [1772539932]})
    pipe = MacroPipe.from_recipes(
        "iso_to_unixtime:value",
    )
    converted_frame = pipe.apply(input_frame.lazy()).collect()
    assert_frame_equal(
        output_frame,
        converted_frame,
    )


def test_unixtime_to_iso():
    """
    Validate converting epoch timestamp (Unix time) to ISO-8601 format.
    """
    input_frame = pl.DataFrame({"value": [1772539932]})
    output_frame = pl.DataFrame({"value": ["2026-03-03T12:12:12.000000"]})
    pipe = MacroPipe.from_recipes(
        "unixtime_to_iso:value",
    )
    converted_frame = pipe.apply(input_frame.lazy()).collect()
    assert_frame_equal(
        output_frame,
        converted_frame,
    )


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
    pipe = MacroPipe.from_recipes(
        "json_array_to_wkt_point:coords",
        "python_to_json:data",
    )
    df = pl.scan_csv(StringIO(csv), quote_char='"')
    df = pipe.apply(df).collect()
    assert_frame_equal(
        df,
        pl.DataFrame(
            {"timestamp": [1754784000000], "coords": ["POINT (9.757 47.389)"], "data": ['{"temperature":42.42}']}
        ),
    )


def test_combine_coords_cells():
    """
    Validate combining two columns into one.
    """
    pytest.importorskip("polars_st")
    csv = """
timestamp,longitude,latitude
1754784000000,9.757,47.389
    """.strip()
    pipe = MacroPipe.from_recipes(
        "columns_to_json_array:longitude,latitude:coords:drop=true",
        "json_array_to_wkt_point:coords",
    )
    df = pl.scan_csv(StringIO(csv))
    df = pipe.apply(df).collect()
    assert_frame_equal(
        df,
        pl.DataFrame({"timestamp": [1754784000000], "coords": ["POINT (9.757 47.389)"]}),
    )


def test_extract_json_columns():
    """
    Validate extracting fields from JSON into columns.
    """
    csv = """
timestamp,data
1754784000000,'{"longitude": 9.757, "latitude": 47.389}'
    """.strip()
    pipe = MacroPipe.from_recipes(
        "json_fields_to_columns:data:longitude,latitude:drop=true",
    )
    df = pl.scan_csv(StringIO(csv), quote_char="'")
    df = pipe.apply(df).collect()
    assert_frame_equal(
        df,
        pl.DataFrame({"timestamp": [1754784000000], "longitude": ["9.757"], "latitude": ["47.389"]}),
    )


def test_extract_json_coords():
    """
    Validate extracting fields from JSON into WKT POINT.
    """
    pytest.importorskip("polars_st")
    csv = """
timestamp,data
1754784000000,"{""lon"": 9.757, ""lat"": 47.389}"
    """.strip()
    pipe = MacroPipe.from_recipes(
        "json_fields_to_wkt_point:data:lon:lat:coords:drop=true",
    )
    df = pl.scan_csv(StringIO(csv))
    df = pipe.apply(df).collect()
    assert_frame_equal(
        df,
        pl.DataFrame({"timestamp": [1754784000000], "coords": ["POINT (9.757 47.389)"]}),
    )
