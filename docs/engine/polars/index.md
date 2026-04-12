(polars-guide)=
# Polars

The Polars engine is currently one of the fastest
data processing solutions on a single machine.

## Introduction

[Polars] has developed its own Domain Specific Language (DSL) for transforming
data. The language is very easy to use and allows for complex queries that
remain human-readable, based on expressions and contexts.

In Polars, an [expression] is a lazy representation of a data transformation.
Expressions are modular and flexible, which means you can use them as building
blocks to build more complex expressions.

Polars features a [lazy API] and [streaming] operations: Your query is only
evaluated once results intend to be acquired, and processing the data in
batches allows working with datasets that do not fit in memory.
Deferring the execution like this can have significant performance advantages.

Using the Polars DSL, you can compose expressions in a fluent way, this is what
you are normally doing when writing Python programs or notebooks. However, you
can also use a structured way, by applying a sequence of user-defined functions
(UDFs) using the [pipe operator].

## About

Tikray/MacroPipe follows the structured pipeline approach provided by Polars'
[pipe operator], providing a miniature transformation engine closely following
Polars' paradigms.

In contrast to the Python-based API, MacroPipe invents a simple textual
macro language that compiles to Polars LazyFrame transformations:
Function name and positional arguments are separated by colons `:`,
that's it.
```text
<function>:<arg1>:<arg2>:<arg3>
```

MacroPipe ships with a few built-in function recipes and allows you to
register transformation functions yourself, based on Polars' powerful
`Expr` primitive and ecosystem.

For Python consumption, Tikray includes the `tikray.macropipe` package that
exports the `MacroPipe` and `recipe` symbols. For Polars consumption,
Tikray registers MacroPipe's methods on the `mp` LazyFrame namespace.

## Install

```shell
pip install --upgrade 'tikray[macropipe]'
```

## Usage

The Polars engine is currently a stand-in. It has not been slotted into the
Tikray data model yet. However, you can already use its Python API like
outlined below.

Let's use an example where you find a CSV file that includes values that need
preprocessing before you can import the dataset into a database. In this case,
you need to perform two transformation steps.

- Convert coordinates in JSON list format to WKT POINT format.
- Convert a dictionary encoded in proprietary Python format into standard JSON format.

The program below implements those requirements pretty concisely, using two
built-in MacroPipe recipes to convert CSV cell values into the required formats.

```python
import polars as pl
from io import StringIO
from tikray.macropipe import MacroPipe

# Define a transformation pipeline using a set of macro/recipe functions.
pipeline = MacroPipe.from_recipes(
    "json_array_to_wkt_point:coordinates",
    "python_to_json:data",
)

# Read CSV data.
lf = pl.scan_csv("example.csv")

# Apply transformation pipeline, compute the result, and inspect the data.
df = lf.mp.apply(pipeline).collect()
print(df)
```

**Input (`example.csv`):**
```csv
timestamp,coordinates,data
1754784000000,"[9.757, 47.389]","{'temperature': 42.42, 'humidity': 84.84}"
```

**Output:**
```csv
timestamp,coordinates,data
1754784000000,"POINT( 9.757 47.389 )","{""temperature"": 42.42, ""humidity"": 84.84}"
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

## Related projects

- [Turtle Island]

## Backlog

See [backlog.md](backlog.md).


[expression]: https://docs.pola.rs/user-guide/concepts/expressions-and-contexts/
[lazy API]: https://docs.pola.rs/user-guide/concepts/lazy-api/
[MacroPipe built-in library]: https://github.com/panodata/tikray/blob/main/src/tikray/macropipe/lib.py
[pipe operator]: https://docs.pola.rs/api/python/stable/reference/expressions/api/polars.Expr.pipe.html
[Polars]: https://pola.rs/
[streaming]: https://docs.pola.rs/user-guide/concepts/streaming/
[Turtle Island]: https://jrycw.github.io/turtle-island/
