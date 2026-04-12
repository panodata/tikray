(polars-guide)=
# Polars

:::{div} sd-text-muted
The MacroPipe transformation engine uses a little text-only
macro language that compiles to Polars expressions.
:::

## Introduction

The Polars engine is currently one of the fastest data processing solutions
on a single machine.

[Polars] has developed its own Domain Specific Language (DSL) for transforming
data. The language is easy to use and allows for complex queries that
remain human-readable, based on expressions and contexts.

In Polars, an _expression_ is a lazy representation of a data transformation.
[Expressions][expr-concept] are modular and flexible, which means you can
use them as building blocks to build more complex expressions.

Polars features a [lazy API] and [streaming] operations: Your query is only
evaluated once results intend to be acquired, and processing the data in
batches allows working with datasets that do not fit in memory.
Deferring the execution like this can have significant performance advantages.

Using the Polars DSL, you can compose expressions in a fluent way, this is what
you are normally doing when writing Python programs or notebooks. However, you
can also use a structured way, by applying a sequence of user-defined functions
(UDFs) using the [pipe operator].

(macropipe)=

## MacroPipe

MacroPipe follows the structured pipeline approach provided by the Polars
[pipe operator]. [^littering]

In contrast to the Python-based API, MacroPipe invents a simple textual
macro language that compiles to Polars LazyFrame transformations:
Function name and positional arguments are separated by colons `:`,
that's it. Use `\:` to represent a literal colon inside an argument. [^macro-next]
```text
<function>:<arg1>:<arg2>:<arg3>
```

MacroPipe ships with a few [built-in function recipes] and allows you to
register transformation functions yourself, based on Polars' powerful
[`Expr`] [primitive][expr-concept] and [ecosystem][expr-types].

> In Polars, an _expression_ is a lazy representation of a data transformation.

For Python consumption, Tikray includes the `tikray.macropipe` package that
exports the `MacroPipe` and `recipe` symbols. For Polars consumption,
Tikray registers MacroPipe's methods on the `mp` LazyFrame namespace.

[^littering]: To support Polars in creating optimal query plans, the current
              implementation will need to get rid of a bit of [pipe littering] that
              crept in. Any support is much appreciated.

[^macro-next]: Currently, the macro language is pretty ~~poor~~ flat.
               It can certainly be improved in future iterations.
               Any suggestions are very much welcome.
               Q: What about [CQL] ([spec][cql-spec]) or related languages?

## Install

```shell
pip install --upgrade 'tikray[macropipe]'
```

## Synopsis

Read from data source, apply transformation, and write to data sink,
in four lines of code.

```python
import polars as pl
from tikray.macropipe import MacroPipe

# Define transformation pipeline.
pipeline = MacroPipe.from_recipes("head:30")

# Invoke pipeline and inspect result.
lf = pl.scan_csv("example.csv")
df = lf.mp.apply(pipeline).collect()
print(df)
```

## Documentation

:::{rubric} Details
:::

The Polars engine is currently a stand-in. It has not been slotted into the
Tikray data model yet. However, you can already use its Python API like
outlined above.

Please inspect the [MacroPipe built-in library] to learn about recipe functions
you can use out of the box. You can add custom transformation functions by
registering them using the `@tikray.macropipe.recipe` Python decorator.

MacroPipe provides a pretty slim textual macro interface by standing on the
shoulders of giants. Required package sizes can weigh in significantly, in
this spirit the subsystem is trading memory for speed.

- https://pypi.org/project/polars/ (45 MB)
- https://pypi.org/project/polars-st/ (50 MB)
- https://pypi.org/project/pyarrow/ (50 MB)
- https://pypi.org/project/pyogrio/ (30 MB)

:::{rubric} Related
:::

- [Turtle Island]
- [LLM DSL for Polars]
- [PEP 638 – Syntactic Macros]
- [`functools.pipe` - Function Composition Utility]
- [data_algebra] is a piped data wrangling system based on Codd's relational algebra

:::{rubric} Backlog
:::

See [backlog.md](backlog.md).

## CSV example

Imagine a CSV file finds you that needs pre-processing before you can import
the dataset into a database.

:::{rubric} Input (`example.csv`)
:::

Your database does not understand the `coordinates` format,
and the `data` values are not using standard JSON format.

```text
timestamp,coordinates,data
1754784000000,"[9.757, 47.389]","{'temperature': 42.42, 'humidity': 84.84}"
```

:::{rubric} Evaluation
:::

In this case, you need to perform two transformation steps.

- Convert coordinates in JSON list format to WKT POINT format.
  ```text
  Input:  [9.757, 47.389]
  Output: POINT( 9.757 47.389 )
  ```
- Convert the data dictionary encoded in proprietary Python format into standard JSON format.
  ```text
  Input:  {'temperature': 42.42, 'humidity': 84.84}
  Output: {"temperature": 42.42, "humidity": 84.84}
  ```

:::{rubric} Implementation
:::

The program below implements those requirements, using two built-in MacroPipe
recipe functions that convert CSV cell values into the required formats.
You can also find the routine in the [macropipe example program].

```python
import polars as pl
from tikray.macropipe import MacroPipe

# Define a transformation pipeline using two recipe functions.
pipeline = MacroPipe.from_recipes(
    "json_array_to_wkt_point:coordinates",
    "python_to_json:data",
)

# Read CSV data.
lf = pl.scan_csv("example.csv")

# Apply transformation pipeline and compute the result.
df = lf.mp.apply(pipeline).collect()
```

:::{rubric} Output
:::

```python
>>> print(df)
```
```text
shape: (1, 3)
┌───────────────┬──────────────────────┬─────────────────────────────────┐
│ timestamp     ┆ coordinates          ┆ data                            │
│ ---           ┆ ---                  ┆ ---                             │
│ i64           ┆ str                  ┆ str                             │
╞═══════════════╪══════════════════════╪═════════════════════════════════╡
│ 1754784000000 ┆ POINT (9.757 47.389) ┆ {"temperature":42.42,"humidity… │
└───────────────┴──────────────────────┴─────────────────────────────────┘
```
```python
>>> print(df.write_csv(include_header=True, quote_style="non_numeric"))
```
```text
"timestamp","coordinates","data"
1754784000000,"POINT (9.757 47.389)","{""temperature"":42.42,""humidity"":84.84}"
```

## Parquet example

:::{rubric} Usage
:::

Imagine a Parquet file where you only want to proceed with a subset of the data,
by filtering records by cell values, and by selecting only specific columns.

The program below implements those requirements, using the built-in MacroPipe
recipe functions `filter` and `select`.
You can also find the routine in the [macropipe example program].

```python
import polars as pl
from tikray.macropipe import MacroPipe

# Define a transformation pipeline using two recipe functions.
pipeline = MacroPipe.from_recipes(
    "filter:total_amount > 40",
    "select:passenger_count,trip_distance,fare_amount,tip_amount,total_amount",
)

# Read Parquet data.
lf = pl.scan_parquet("https://cdn.crate.io/downloads/datasets/cratedb-datasets/timeseries/yc.2019.07-tiny.parquet")

# Apply transformation pipeline and compute the result.
df = lf.mp.apply(pipeline).collect()
```

:::{rubric} Output
:::

```python
>>> print(df)
```
```text
Output: shape: (4, 5)
┌─────────────────┬───────────────┬─────────────┬────────────┬──────────────┐
│ passenger_count ┆ trip_distance ┆ fare_amount ┆ tip_amount ┆ total_amount │
│ ---             ┆ ---           ┆ ---         ┆ ---        ┆ ---          │
│ i64             ┆ f64           ┆ f64         ┆ f64        ┆ f64          │
╞═════════════════╪═══════════════╪═════════════╪════════════╪══════════════╡
│ 1               ┆ 18.8          ┆ 52.0        ┆ 11.75      ┆ 70.67        │
│ 1               ┆ 18.46         ┆ 52.0        ┆ 11.06      ┆ 66.36        │
│ 1               ┆ 7.0           ┆ 24.5        ┆ 6.85       ┆ 41.27        │
│ 1               ┆ 10.3          ┆ 31.5        ┆ 8.8        ┆ 44.1         │
└─────────────────┴───────────────┴─────────────┴────────────┴──────────────┘
```
```python
>>> print(df.write_csv(include_header=True, quote_style="non_numeric"))
```
```text
"passenger_count","trip_distance","fare_amount","tip_amount","total_amount"
1,18.8,52.0,11.75,70.67
1,18.46,52.0,11.06,66.36
1,7.0,24.5,6.85,41.27
1,10.3,31.5,8.8,44.1
```



[built-in function recipes]: https://github.com/panodata/tikray/blob/main/src/tikray/macropipe/lib.py
[CQL]: https://en.wikipedia.org/wiki/Contextual_Query_Language
[cql-spec]: https://www.loc.gov/standards/sru/cql/spec.html
[data_algebra]: https://github.com/WinVector/data_algebra
[`Expr`]: https://docs.pola.rs/api/rust/dev/polars_lazy/dsl/enum.Expr.html
[expr-concept]: https://docs.pola.rs/user-guide/concepts/expressions-and-contexts/
[expr-types]: https://docs.pola.rs/user-guide/expressions/
[`functools.pipe` - Function Composition Utility]: https://discuss.python.org/t/functools-pipe-function-composition-utility/69744
[lazy API]: https://docs.pola.rs/user-guide/concepts/lazy-api/
[LLM DSL for Polars]: https://www.linkedin.com/pulse/dsls-llms-ken-kocienda-fpi1c
[MacroPipe built-in library]: https://github.com/panodata/tikray/blob/main/src/tikray/macropipe/lib.py
[macropipe example program]: https://github.com/panodata/tikray/blob/main/examples/api/macropipe.py
[PEP 638 – Syntactic Macros]: https://peps.python.org/pep-0638/
[pipe littering]: https://docs.pola.rs/user-guide/migration/pandas/#pipe-littering
[pipe operator]: https://docs.pola.rs/api/python/stable/reference/lazyframe/api/polars.LazyFrame.pipe.html
[Polars]: https://pola.rs/
[streaming]: https://docs.pola.rs/user-guide/concepts/streaming/
[Turtle Island]: https://jrycw.github.io/turtle-island/
