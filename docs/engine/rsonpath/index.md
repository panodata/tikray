(rsonpath-guide)=
# rsonpath

Yet another rsonpath cheat sheet.

## Introduction

[rsonpath] is a blazing fast JSONPath query engine written in Rust.
It allows to run structure-aware JSONPath queries on JSON data
as easily as one would query a string with regular expressions.
The [JSONPath standard] defines a query expression syntax for
selecting and extracting JSON values from within a given JSON
value.
[rsonpy] is a lightweight Python wrapper around the Rust library.

To learn fundamentals about rsonpath, please refer to the [rsonbook],
and specifically the [JSONPath reference].

:::{rubric} Use cases
:::

> Rsonpath is made to filter document ahead of parsing/loading. Think of
it like a way to select a small part of the documents before
loading it into memory. It will shine in situations where you have a
JSON file too big to hold in memory, but you nevertheless want to load
parts of it.

> Rsonpath does not load anything into memory.
> It only works on the raw JSON, not on an in-memory data structure.

:::{rubric} jqlang vs. rsonpath
:::

If you are asking what's wrong with `jq`, the authors provide
concise answers per [Why choose rsonpath?]:

> The most popular tool for working with JSON data is [jq], but it has
a few shortcomings:
>
> - it is _extremely_ slow
> - it has a _massive_ memory overhead
> - its query language is non-standard.
>
> To be clear, `jq` is a great and well-tested tool, and `rq` does not
directly compete with it. If one could describe `jq` as a “sed or awk
for JSON”, then `rq` would be a “grep for JSON”: It does not allow you
to slice and reorganize JSON data like `jq`, but instead outclasses it
on the filtering and querying applications.


## Examples

### Unwrap

::::::{card}
It is typical for HTTP JSON API responses to not start directly with a
collection of data items, because a typical response also includes other
metadata. In this spirit, when connecting pipeline elements of JSON
processors, input data mostly needs to be edited into a variant suitable
for storing into a database, likely also transitioning from a top-level
object to a top-level list.
- Unwrap the actual collection which is nested within the top-level `records` element.
- Flatten the element `nested-list` which contains nested lists.
```yaml
expression: $.records
type: rson
```
:::::{dropdown} Example
:margin: 0

::::{grid} 2
:gutter: 0
:margin: 0
:padding: 0

:::{grid-item-card}
:margin: 0
:padding: 0
Input data
```json
{
  "message-source": "community",
  "message-type": "mixed-pickles",
  "records": [
    {"foo": "bar"},
    {"baz": "qux"}
  ]
}
```
:::
:::{grid-item-card}
:margin: 0
:padding: 0
Output data
```json
[
  {"foo": "bar"},
  {"baz": "qux"}
]
```
:::

:::{grid-item-card}
:margin: 0
:padding: 0
:columns: 12
Transformation definition
```{code-block} yaml
# Tikray collection-level transformation definition.
# Includes a Moksha/rsonpath transformation rule for unwrapping and flattening.
# https://tikray.readthedocs.io/
---
meta:
  type: tikray-collection
  version: 1
pre:
  rules:
  - expression: $.records
    type: rson
```
:::

::::
:::::
::::::


[jq]: https://jqlang.org/
[JSONPath reference]: https://rsonquery.github.io/rsonpath/user/usage/jsonpath.html
[JSONPath standard]: https://www.rfc-editor.org/rfc/rfc9535.html
[rsonpath]: https://github.com/rsonquery/rsonpath
[rsonpy]: https://github.com/rsonquery/rsonpy
[rsonbook]: https://rsonquery.github.io/rsonpath/
[Why choose rsonpath?]: https://rsonquery.github.io/rsonpath/#why-choose-rsonpath
