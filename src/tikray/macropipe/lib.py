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

    def apply(self, pipe) -> pl.LazyFrame:
        """Convert transformation recipes to Polars expressions and apply to structured pipeline."""
        return pipe.apply(self._lf)

    def head(self, n: str) -> pl.LazyFrame:
        """
        Get the first `n` rows.

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

        TODO: Improve with automatic frame method mapping, see `head`.
        """
        return self._lf.tail(int(n))

    def first(self) -> pl.LazyFrame:
        """
        Get the first value.

        TODO: Improve with automatic frame method mapping, see `head`.
        """
        return self._lf.first()

    def last(self) -> pl.LazyFrame:
        """
        Get the last value.

        TODO: Improve with automatic frame method mapping, see `head`.
        """
        return self._lf.last()

    def cast(self, column_names: t.Union[str, t.List[str]], dtype: str) -> pl.LazyFrame:
        """
        Cast multiple columns by type name, separated by commas.
        """
        lf = self._lf
        column_names = decode_list(column_names)
        for column_name in column_names:
            dtype_real = pl.DataType.from_python(gettype(dtype))
            lf = lf.with_columns(pl.col(column_name).cast(dtype=dtype_real))
        return lf

    def select(self, column_names: t.Union[str, t.List[str]]) -> pl.LazyFrame:
        """
        Select multiple columns by name, separated by commas.
        """
        column_names = decode_list(column_names)
        return self._lf.select(*column_names)

    def drop(self, column_names: t.Union[str, t.List[str]]) -> pl.LazyFrame:
        """
        Drop multiple columns by name, separated by commas.
        """
        column_names = decode_list(column_names)
        return self._lf.drop(*column_names)

    def rename(self, source_column: str, target_column: str) -> pl.LazyFrame:
        """
        Rename a single column.
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
        Combine multiple columns by joining them, separated by commas.
        """
        column_names = decode_list(column_names)
        lf = self._lf.with_columns(pl.concat_str(column_names, separator=separator).alias(target_column))
        if options and "drop=true" in options:
            lf = lf.drop(*column_names)
        return lf

    def format(
        self,
        f_string: str,
        column_names: t.Union[str, t.List[str]],
        target_column: str,
        options: t.Optional[str] = None,
    ) -> pl.LazyFrame:
        """
        Format expressions as a string.

        "format:foo_{}_bar_{}:a,b:value:drop=true"
        """
        column_names = decode_list(column_names)
        lf = self._lf.with_columns(pl.format(f_string, *column_names).alias(target_column))
        if options and "drop=true" in options:
            lf = lf.drop(*column_names)
        return lf

    def scale(self, column_name: str, factor: float) -> pl.LazyFrame:
        """
        Scale a single column.
        """
        return self._lf.with_columns(pl.col(column_name).truediv(float(factor)))

    def iso_to_unixtime(self, column_name: str) -> pl.LazyFrame:
        """
        Convert ISO 8601 / RFC 3339 date & time format to epoch timestamp (Unix time).
        """
        return self._lf.with_columns(pl.col(column_name).dt.epoch(time_unit="s"))

    def unixtime_to_iso(self, column_name: str) -> pl.LazyFrame:
        """
        Convert epoch timestamp (Unix time) to ISO 8601 / RFC 3339 date & time format.

        Example: 2026-03-03T12:12:12.000000
        """
        return self._lf.with_columns(pl.from_epoch(pl.col(column_name)).dt.to_string(format="iso:strict"))

    def json_array_to_wkt_point(self, col_name: str) -> pl.LazyFrame:
        """
        Convert coordinates list `[long, lat]` in JSON format to WKT `POINT (long lat)` format.

        Input:  "[9.757, 47.389]"
        Output: "POINT ( 9.757 47.389 )"
        """
        import polars_st as st

        return self._lf.with_columns(st.point(pl.col(col_name).str.json_decode(dtype=pl.List(pl.Float64))).st.to_wkt())

    def python_to_json(self, col_name: str) -> pl.LazyFrame:
        """
        Convert Python-encoded dictionary into pure JSON.

        Input:  "{'temperature': 42.42}"
        Output: '{"temperature": 42.42}'
        """
        return self._lf.with_columns(
            pl.col(col_name).map_elements(lambda x: orjson.dumps(ast.literal_eval(x)).decode(), return_dtype=pl.String)
        )

    def columns_to_json_array(
        self, source_columns: t.Union[str, t.List[str]], target_column: str, options: t.Optional[str] = None
    ) -> pl.LazyFrame:
        """
        Combine individual columns into JSON-encoded array.

        Input:  longitude,latitude
                9.757,47.389
        Output: coordinates
                "[9.757 47.389]"
        """
        source_columns = decode_list(source_columns)
        lf = self._lf.with_columns(
            pl.concat_list(pl.col(*source_columns)).struct.json_encode().alias(target_column),
        )
        if options and "drop=true" in options:
            lf = lf.drop(*source_columns)
        return lf

    def json_fields_to_columns(
        self, source_column: str, extract_columns: t.Union[str, t.List[str]], options: t.Optional[str] = None
    ) -> pl.LazyFrame:
        """
        Extract JSON fields into individual columns.

        Input:  '{"longitude": 9.757, "latitude": 47.389}'
        Output: longitude,latitude
                9.757,47.389
        """
        lf = self._lf
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

        Input:  '{"longitude": 9.757, "latitude": 47.389}'
                9.757,47.389
        Output: coords
                "POINT ( 9.757 47.389 )"
        """
        import polars_st as st

        lf = self.json_fields_to_columns(source_column, [longitude_field, latitude_field])
        lf = lf.with_columns(
            st.point(pl.concat_arr(pl.col(longitude_field), pl.col(latitude_field))).st.to_wkt().alias(target_column),
        )
        lf = lf.drop(longitude_field, latitude_field)
        if options and "drop=true" in options:
            lf = lf.drop(source_column)
        return lf
