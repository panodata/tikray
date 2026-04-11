import ast
import pydoc
import typing as t

import orjson
import polars as pl
from polars._typing import PythonDataType

from tikray.macropipe.core import recipe


def decode_list(data: t.Union[str, t.List[str]]) -> t.List[str]:
    if isinstance(data, str):
        return list(map(str.strip, data.split(",")))
    return data


def gettype(name: str) -> PythonDataType:
    """
    Lexical cast from string to type.
    https://stackoverflow.com/a/29831586
    """
    return t.cast(PythonDataType, pydoc.locate(name))


@recipe
def cast(lf: pl.LazyFrame, column_names: t.Union[str, t.List[str]], dtype: str) -> pl.LazyFrame:
    """
    Cast multiple columns by type name, separated by commas.
    """
    column_names = decode_list(column_names)
    for column_name in column_names:
        dtype_real = pl.DataType.from_python(gettype(dtype))
        lf = lf.with_columns(pl.col(column_name).cast(dtype=dtype_real))
    return lf


@recipe
def select(lf: pl.LazyFrame, column_names: t.Union[str, t.List[str]]) -> pl.LazyFrame:
    """
    Select multiple columns by name, separated by commas.
    """
    column_names = decode_list(column_names)
    return lf.select(*column_names)


@recipe
def drop(lf: pl.LazyFrame, column_names: t.Union[str, t.List[str]]) -> pl.LazyFrame:
    """
    Drop multiple columns by name, separated by commas.
    """
    column_names = decode_list(column_names)
    return lf.drop(*column_names)


@recipe
def rename(lf: pl.LazyFrame, source_column: str, target_column: str) -> pl.LazyFrame:
    """
    Rename a single column.
    """
    return lf.rename({source_column: target_column})


@recipe
def concat(
    lf: pl.LazyFrame,
    column_names: t.Union[str, t.List[str]],
    separator: str,
    target_column: str,
    options: t.Optional[str] = None,
) -> pl.LazyFrame:
    """
    Combine multiple columns by joining them, separated by commas.
    """
    column_names = decode_list(column_names)
    lf = lf.with_columns(pl.concat_str(column_names, separator=separator).alias(target_column))
    if options and "drop=true" in options:
        lf = lf.drop(*column_names)
    return lf


@recipe
def scale(lf: pl.LazyFrame, column_name: str, factor: float) -> pl.LazyFrame:
    """
    Scale a single column.
    """
    return lf.with_columns(pl.col(column_name).truediv(int(factor)))


@recipe
def iso_to_unixtime(lf: pl.LazyFrame, column_name: str) -> pl.LazyFrame:
    """
    Convert ISO 8601 / RFC 3339 date & time format to epoch timestamp (Unix time).
    """
    return lf.with_columns(pl.col(column_name).dt.epoch(time_unit="s"))


@recipe
def unixtime_to_iso(lf: pl.LazyFrame, column_name: str) -> pl.LazyFrame:
    """
    Convert epoch timestamp (Unix time) to ISO 8601 / RFC 3339 date & time format.

    Example: 2026-03-03T12:12:12.000000
    """
    return lf.with_columns(pl.from_epoch(pl.col(column_name)).dt.to_string(format="iso:strict"))


@recipe
def json_array_to_wkt_point(lf: pl.LazyFrame, col_name: str) -> pl.LazyFrame:
    """
    Convert coordinates list `[long, lat]` in JSON format to WKT `POINT (long lat)` format.

    Input:  "[9.757, 47.389]"
    Output: "POINT ( 9.757 47.389 )"
    """
    import polars_st as st

    return lf.with_columns(st.point(pl.col(col_name).str.json_decode(dtype=pl.List(pl.Float64))).st.to_wkt())


@recipe
def python_to_json(lf: pl.LazyFrame, col_name: str) -> pl.LazyFrame:
    """
    Convert Python-encoded dictionary into pure JSON.

    Input:  "{'temperature': 42.42}"
    Output: '{"temperature": 42.42}'
    """
    return lf.with_columns(
        pl.col(col_name).map_elements(lambda x: orjson.dumps(ast.literal_eval(x)).decode(), return_dtype=pl.String)
    )


@recipe
def columns_to_json_array(
    lf: pl.LazyFrame, source_columns: t.Union[str, t.List[str]], target_column: str, options: t.Optional[str] = None
) -> pl.LazyFrame:
    """
    Combine individual columns into JSON-encoded array.

    Input:  longitude,latitude
            9.757,47.389
    Output: coordinates
            "[9.757 47.389]"
    """
    source_columns = decode_list(source_columns)
    lf = lf.with_columns(
        pl.concat_list(pl.col(*source_columns)).struct.json_encode().alias(target_column),
    )
    if options and "drop=true" in options:
        lf = lf.drop(*source_columns)
    return lf


@recipe
def json_fields_to_columns(
    lf: pl.LazyFrame, source_column: str, extract_columns: t.Union[str, t.List[str]], options: t.Optional[str] = None
) -> pl.LazyFrame:
    """
    Extract JSON fields into individual columns.

    Input:  '{"longitude": 9.757, "latitude": 47.389}'
    Output: longitude,latitude
            9.757,47.389
    """
    extract_columns = decode_list(extract_columns)
    for extract_column in extract_columns:
        lf = lf.with_columns(
            pl.col(source_column)
            .str.json_decode(dtype=pl.Struct({extract_column: pl.String}))
            .struct.field(extract_column),
        )
    if options and "drop=true" in options:
        lf = lf.drop(source_column)
    return lf


@recipe
def json_fields_to_wkt_point(
    lf: pl.LazyFrame,
    source_column: str,
    longitude_field: str,
    latitude_field: str,
    target_column: str,
    options: t.Optional[str] = None,
) -> pl.LazyFrame:
    """
    Extract longitude and latitude fields from JSON and encode them into WKT POINT format.

    Input:  '{"longitude": 9.757, "latitude": 47.389}'
            9.757,47.389
    Output: coords
            "POINT ( 9.757 47.389 )"
    """
    import polars_st as st

    lf = json_fields_to_columns(lf, source_column, [longitude_field, latitude_field])
    lf = lf.with_columns(
        st.point(pl.concat_arr(pl.col(longitude_field), pl.col(latitude_field))).st.to_wkt().alias(target_column),
    )
    lf = lf.drop(longitude_field, latitude_field)
    if options and "drop=true" in options:
        lf = lf.drop(source_column)
    return lf
