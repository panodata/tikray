"""
# MacroPipe examples

- Convert a CSV file with special features for importing into CrateDB.
- Filter a Parquet file to only proceed with a subset of the data.
"""

from io import StringIO

import polars as pl

from tikray.macropipe import MacroPipe


def csv_example():
    """
    Convert a CSV file with special features for importing into CrateDB.
    The procedure applies two transformations before the data is ready.

    - Convert coordinates in JSON list format to WKT POINT format.
    - Convert a dictionary encoded in proprietary Python format into standard JSON format.

    - https://github.com/crate/crate-clients-tools/issues/319
    - https://gist.github.com/amotl/949547787e116c8cafabe2959281e7ec
    """

    input_data = """
timestamp,coordinates,data
1754784000000,"[9.757, 47.389]","{'temperature': 42.42, 'humidity': 84.84}"
    """.strip()
    input_frame = pl.scan_csv(StringIO(input_data), quote_char='"')

    pipe = MacroPipe.from_recipes(
        "json_array_to_wkt_point:coordinates",
        "python_to_json:data",
    )
    output_frame = pipe.apply(input_frame)

    header("CSV example")
    print("Input: ", input_frame.collect())
    print("Output:", output_frame.collect())
    print()
    print("Input CSV:")
    print(input_data)
    print()
    print("Output CSV:")
    print(output_frame.collect().write_csv(quote_style="non_numeric"))
    print()


def parquet_example():
    """
    Filter a Parquet file to only proceed with a subset of the data.
    """

    input_frame = pl.scan_parquet(
        "https://cdn.crate.io/downloads/datasets/cratedb-datasets/timeseries/yc.2019.07-tiny.parquet"
    )

    pipe = MacroPipe.from_recipes(
        "filter:total_amount > 40",
        "select:passenger_count,trip_distance,fare_amount,tip_amount,total_amount",
    )
    output_frame = pipe.apply(input_frame)

    header("Parquet example")
    print("Input: ", input_frame.collect())
    print("Output:", output_frame.collect())
    print()
    print("Output CSV:")
    print(output_frame.collect().write_csv(quote_style="non_numeric"))
    print()


def header(text: str):
    """Print a header to the screen."""
    width = 100
    print("=" * width)
    print(text.center(width))
    print("=" * width)
    print()


if __name__ == "__main__":
    csv_example()
    parquet_example()
