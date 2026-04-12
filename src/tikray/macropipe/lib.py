import ast
import typing as t

import orjson
import polars as pl

from tikray.macropipe.util import decode_list, gettype


@pl.api.register_lazyframe_namespace("mp")
class MacroPipeBuiltins:
    """
    https://docs.pola.rs/api/python/stable/reference/api/polars.api.register_lazyframe_namespace.html
    """

    def __init__(self, lf: pl.LazyFrame) -> None:
        self._lf = lf

    @staticmethod
    def _drop_if_requested(lf: pl.LazyFrame, options: t.Optional[str], columns: t.List[str]) -> pl.LazyFrame:
        """Drop columns when `drop=true` is present in the options string."""
        if options and "drop=true" in options:
            return lf.drop(*columns)
        return lf

    def apply(self, pipe) -> pl.LazyFrame:
        """Convert transformation recipes to Polars expressions and apply to structured pipeline."""
        return pipe.apply(self._lf)

    def head(self, n: str) -> pl.LazyFrame:
        """
        Get the first `n` rows.

        Input:  All records.
        Recipe: "head:1"
        Output: Filtered records.

        TODO: Q: Can such primitives that barely need any argument processing be mapped directly?
              A: Well, because of the macro nature, at least all types must be casted appropriately
                 from `str`. This is an excellent example where only a single argument needs to be
                 processed. Maybe we can invent some automatic mapping, so we don't need to enumerate
                 and map Polars' frame methods manually.
        """
        return self._lf.head(int(n))

    def tail(self, n: str) -> pl.LazyFrame:
        """
        Get the last `n` rows.

        Input:  All records.
        Recipe: "tail:1"
        Output: Filtered records.

        TODO: Improve with automatic frame method mapping, see `head`.
        """
        return self._lf.tail(int(n))

    def first(self) -> pl.LazyFrame:
        """
        Get the first value.

        Input:  All records.
        Recipe: "first"
        Output: Filtered records.

        TODO: Improve with automatic frame method mapping, see `head`.
        """
        return self._lf.first()

    def last(self) -> pl.LazyFrame:
        """
        Get the last value.

        Input:  All records.
        Recipe: "last"
        Output: Filtered records.

        TODO: Improve with automatic frame method mapping, see `head`.
        """
        return self._lf.last()

    def cast(self, column_names: t.Union[str, t.List[str]], dtype: str) -> pl.LazyFrame:
        """
        Cast multiple columns by type name.

        Input:  {"float": 42.42, "int": 42, "str": "42"}
        Recipe: "cast:float,int,str:float"
        Output: {"float": 42.42, "int": 42.0, str: 42.0}
        """
        column_names = decode_list(column_names)
        dtype_real = pl.DataType.from_python(gettype(dtype))
        return self._lf.with_columns([pl.col(col).cast(dtype=dtype_real) for col in column_names])

    def select(self, column_names: t.Union[str, t.List[str]]) -> pl.LazyFrame:
        """
        Select multiple columns by name.

        Input:  {"ts": 1754784000000, "data": "Hotzenplotz", "foo": "42"}
        Recipe: "select:ts,data"
        Output: {"ts": 1754784000000, "data": "Hotzenplotz"}
        """
        column_names = decode_list(column_names)
        return self._lf.select(*column_names)

    def drop(self, column_names: t.Union[str, t.List[str]]) -> pl.LazyFrame:
        """
        Drop multiple columns by name.

        Input:  {"ts": 1754784000000, "data": "Hotzenplotz", "foo": "42"}
        Recipe: "drop:foo"
        Output: {"ts": 1754784000000, "data": "Hotzenplotz"}
        """
        column_names = decode_list(column_names)
        return self._lf.drop(*column_names)

    def rename(self, source_column: str, target_column: str) -> pl.LazyFrame:
        """
        Rename a single column.

        Input:  {"_id": "01kp0w38"}
        Recipe: "rename:_id:__id"
        Output: {"__id": "01kp0w38"}
        """
        return self._lf.rename({source_column: target_column})

    def concat(
        self,
        column_names: t.Union[str, t.List[str]],
        separator: str,
        target_column: str,
        options: t.Optional[str] = None,
    ) -> pl.LazyFrame:
        """
        Combine multiple columns by joining them. Optionally drop the original columns.

        Input:  {"firstname": "Räuber", "lastname": "Hotzenplotz"}
        Recipe: "concat:firstname,lastname: :combined:drop=true"
        Output: {"name": "Räuber Hotzenplotz"}
        """
        column_names = decode_list(column_names)
        lf = self._lf.with_columns(pl.concat_str(column_names, separator=separator).alias(target_column))
        return self._drop_if_requested(lf, options, column_names)

    def format(
        self,
        f_string: str,
        column_names: t.Union[str, t.List[str]],
        target_column: str,
        options: t.Optional[str] = None,
    ) -> pl.LazyFrame:
        """
        Derive a new column by applying a format expressions to existing columns. Optionally drop the original columns.

        Input:  {"a": ["a", "b", "c"], "b": [1, 2, 3]}
        Recipe: "format:foo_{}_bar_{}:a,b:value:drop=true"
        Output: {"value": ["foo_a_bar_1", "foo_b_bar_2", "foo_c_bar_3"]}
        """
        column_names = decode_list(column_names)
        lf = self._lf.with_columns(pl.format(f_string, *column_names).alias(target_column))
        return self._drop_if_requested(lf, options, column_names)

    def filter(self, sql: str) -> pl.LazyFrame:
        """
        Transform result by filtering records using SQL WHERE expression clauses.

        https://docs.pola.rs/user-guide/sql/intro/
        https://docs.pola.rs/user-guide/transformations/time-series/filter/
        https://docs.pola.rs/api/python/stable/reference/expressions/api/polars.sql_expr.html

        Input:  [{"ts": 1754784000000, "data": "foo"}, {"ts": 1754785000000, "data": "bar"}]
        Recipe: "filter:ts < 1754785000000"
        Output: [{"ts": 1754784000000, "data": "foo"}]
        """
        return self._lf.filter(pl.sql_expr(sql))

    def scale(self, column_name: str, factor: float) -> pl.LazyFrame:
        """
        Scale value in a single column by multiplying by a factor.

        Input:  {"value": 4242}
        Recipe: "scale:value:0.01"
        Output: {"value": 42.42}
        """
        return self._lf.with_columns(pl.col(column_name).mul(float(factor)))

    def iso_to_unixtime(self, column_name: str) -> pl.LazyFrame:
        """
        Convert ISO 8601 / RFC 3339 date & time format to epoch timestamp (Unix time).

        Input:  {"value": "2026-03-03T12:12:12"}
        Recipe: "iso_to_unixtime:value"
        Output: {"value": 1772539932}
        """
        return self._lf.with_columns(pl.col(column_name).str.to_datetime().dt.epoch(time_unit="s"))

    def unixtime_to_iso(self, column_name: str) -> pl.LazyFrame:
        """
        Convert epoch timestamp (Unix time) to ISO 8601 / RFC 3339 date & time format.

        Input:  {"value": 1772539932}
        Recipe: "unixtime_to_iso:value"
        Output: {"value": "2026-03-03T12:12:12.000000"}
        """
        return self._lf.with_columns(pl.from_epoch(pl.col(column_name)).dt.to_string(format="iso:strict"))

    def json_array_to_wkt_point(self, col_name: str) -> pl.LazyFrame:
        """
        Convert coordinates list `[long, lat]` in JSON format to WKT `POINT (long lat)` format.

        Input:  {"coordinates": "[9.757, 47.389]"}
        Recipe: "json_array_to_wkt_point:coordinates"
        Output: {"coordinates": "POINT ( 9.757 47.389 )"}
        """
        import polars_st as st

        return self._lf.with_columns(st.point(pl.col(col_name).str.json_decode(dtype=pl.List(pl.Float64))).st.to_wkt())

    def python_to_json(self, col_name: str) -> pl.LazyFrame:
        """
        Convert Python-encoded dictionary into pure JSON.

        Note: The `python_to_json` method uses `ast.literal_eval()` which, while safer
              than `eval()`, still parses arbitrary Python literal expressions from
              input data. Additionally, `map_elements` disables Polars' parallelization.

        Input:  {"data": "{'temperature': 42.42}"}
        Recipe: "python_to_json:data"
        Output: {"data": '{"temperature": 42.42}'}
        """
        return self._lf.with_columns(
            pl.col(col_name).map_elements(lambda x: orjson.dumps(ast.literal_eval(x)).decode(), return_dtype=pl.String)
        )

    def columns_to_json_array(
        self, source_columns: t.Union[str, t.List[str]], target_column: str, options: t.Optional[str] = None
    ) -> pl.LazyFrame:
        """
        Combine individual columns into JSON-encoded array. Optionally drop the original columns.

        Input:  {"longitude": 9.757, "latitude": 47.389}"}
        Recipe: "columns_to_json_array:longitude,latitude:coordinates:drop=true"
        Output: {"coordinates": "[9.757 47.389]"}
        """
        source_columns = decode_list(source_columns)
        lf = self._lf.with_columns(
            pl.concat_list(pl.col(*source_columns)).struct.json_encode().alias(target_column),
        )
        return self._drop_if_requested(lf, options, source_columns)

    def json_fields_to_columns(
        self,
        source_column: str,
        extract_columns: t.Union[str, t.List[str]],
        dtype: str,
        options: t.Optional[str] = None,
    ) -> pl.LazyFrame:
        """
        Extract JSON fields from single column into individual columns. Optionally drop the original column.

        Input:  {"data": '{"longitude": 9.757, "latitude": 47.389, "more": "anything"}'}
        Recipe: "json_fields_to_columns:data:longitude,latitude:float:drop=true"
        Output: {"longitude": 9.757, "latitude": 47.389}

        TODO: An advanced version could provide extracting individual columns with individual dtypes.
        """
        extract_columns = decode_list(extract_columns)
        dtype_real = pl.DataType.from_python(gettype(dtype))
        lf = self._lf
        for extract_column in extract_columns:
            lf = lf.with_columns(
                pl.col(source_column)
                .str.json_decode(dtype=pl.Struct({extract_column: dtype_real}))
                .struct.field(extract_column),
            )
        return self._drop_if_requested(lf, options, [source_column])

    def json_fields_to_wkt_point(
        self,
        source_column: str,
        longitude_field: str,
        latitude_field: str,
        target_column: str,
        options: t.Optional[str] = None,
    ) -> pl.LazyFrame:
        """
        Extract longitude and latitude fields from JSON and encode them into WKT POINT format.
        Optionally drop the original columns.

        Input:  {"data": '{"longitude": 9.757, "latitude": 47.389}'}
        Recipe: "json_fields_to_wkt_point:data:longitude:latitude:coordinates:drop=true"
        Output: {"coordinates": "POINT ( 9.757 47.389 )"}
        """
        import polars_st as st

        decoded = pl.col(source_column).str.json_decode(
            dtype=pl.Struct(
                {
                    longitude_field: pl.Float64,
                    latitude_field: pl.Float64,
                }
            )
        )
        lf = self._lf.with_columns(
            st.point(
                pl.concat_arr(
                    decoded.struct.field(longitude_field),
                    decoded.struct.field(latitude_field),
                )
            )
            .st.to_wkt()
            .alias(target_column)
        )
        return self._drop_if_requested(lf, options, [source_column])
