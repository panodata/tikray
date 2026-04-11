(polars-guide)=
# Polars

The Polars engine is currently one of the fastest data processing solutions on a single machine.

## Introduction

[Polars] has developed its own Domain Specific Language (DSL) for transforming
data. The language is very easy to use and allows for complex queries that
remain human-readable, based on expressions and contexts.

In Polars, an [expression] is a lazy representation of a data transformation.
Expressions are modular and flexible, which means you can use them as building
blocks to build more complex expressions.

Polars features a [lazy API], where the query is only evaluated once it is
collected. Deferring the execution to the last minute can have significant
performance advantages.

## About

Tikray includes the `tikray.macropipe` package: `MacroPipe` is a miniature
transformation engine based on Polars, accompanied by the `recipe` decorator
to register composite transformation functions.

## Install

```shell
pip install --upgrade 'tikray[macropipe]'
```

## Usage

The Polars engine is currently a stand-in. It has not been slotted into the
Tikray data model yet. However, you can already use its Python API like
outlined below.

```csv
timestamp,coordinates,data
1754784000000,"[9.757, 47.389]","{'temperature': 42.42, 'humidity': 84.84}"
```

```python
import polars as pl
from io import StringIO
from tikray.macropipe import MacroPipe

# Define transformation pipeline made of macro/recipe functions.
pipe = MacroPipe.from_recipes(
    "json_array_to_wkt_point:coordinates",
    "python_to_json:data",
)

# Read CSV data.
lf = pl.scan_csv("example.csv", quote_char='"')

# Apply transformation and inspect data.
df = pipe.process(lf).collect()
print(df)
```

## Details

Please inspect the [MacroPipe built-in library] to learn about recipe functions
you can use out of the box. You can add custom transformation functions by
registering them using the `@tikray.macropipe.recipe` Python decorator.

Please also note while MacroPipe provides a pretty slim textual macro interface,
it is standing on the shoulders of giants. Required packages weigh in significantly,
in this spirit the subsystem is trading memory for speed.

- https://pypi.org/project/polars/ (45 MB)
- https://pypi.org/project/polars-st/ (50 MB)
- https://pypi.org/project/pyarrow/ (50 MB)
- https://pypi.org/project/pyogrio/ (30 MB)


[expression]: https://docs.pola.rs/user-guide/concepts/expressions-and-contexts/
[lazy API]: https://docs.pola.rs/user-guide/concepts/lazy-api/
[MacroPipe built-in library]: https://github.com/panodata/tikray/blob/main/src/tikray/macropipe/lib.py
[Polars]: https://pola.rs/
