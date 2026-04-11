"""
Convert a CSV file with special features for importing into CrateDB.
The procedure applies two transformations before the data is ready.

- Convert coordinates in JSON list format to WKT POINT format.
- Convert a dictionary encoded in proprietary Python format into standard JSON format.

- https://github.com/crate/crate-clients-tools/issues/319
- https://gist.github.com/amotl/949547787e116c8cafabe2959281e7ec
"""

from io import StringIO

import polars as pl

from tikray.macropipe import MacroPipe

CSV_DATA = """
timestamp,coordinates,data
1754784000000,"[9.757, 47.389]","{'temperature': 42.42, 'humidity': 84.84}"
""".strip()


def main():
    pipe = MacroPipe.from_recipes(
        "json_array_to_wkt_point:coordinates",
        "python_to_json:data",
    )
    input_frame = pl.scan_csv(StringIO(CSV_DATA), quote_char='"')
    output_frame = pipe.apply(input_frame)

    print("Input: ", input_frame.collect())
    print("Output:", output_frame.collect())
    print()
    print("Input CSV:")
    print(CSV_DATA)
    print()
    print("Output CSV:")
    print(output_frame.collect().write_csv(quote_style="non_numeric"))


if __name__ == "__main__":
    main()
