(jq-guide)=
# jqlang

Yet another jqlang cheat sheet.

## Introduction

[jq] is like `sed` for JSON data - you can use it to slice and filter and map
and transform structured data with the same ease that `sed`, `awk`, `grep` and
friends let you play with text.
To learn fundamentals about jqlang, the expression language provided by jq,
please refer to the [jq tutorial] and the [jq manual] documentation, and do
a few orientation flights on the [jq playground].

The jqlang expressions on this page focus on common usage with Tikray,
specifically its [jq's update operator] `|=`, as well as
[jq's built-in functions] and [Tikray's jqlang standard library],
including a few support functions you may find useful.
Contributions to them are always welcome.

## Structure

Structural reshaping of nested data before actually processing records is needed
in many cases, for example by applying destructuring, flattening, un-nesting, or
other unwrapping operations to top-level elements or substructures.
Editing the structure mostly applies to container elements `object` and `array`.

### Unwrap and flatten

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
expression: .records[] | ."nested-list" |= flatten
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
    {"nested-list": [{"foo": 1}, [{"foo": 2}, {"foo": 3}]]}
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
  {"nested-list": [{"foo": 1}, {"foo": 2}, {"foo": 3}]}
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
# Includes a Moksha/jq transformation rule for unwrapping and flattening.
# https://tikray.readthedocs.io/
---
meta:
  type: tikray-collection
  version: 1
pre:
  rules:
  - expression: .records[] | ."nested-list" |= flatten
    type: jq
```
:::

::::
:::::
::::::

### Select elements

::::::{card}
Select object attributes by path, also multiple ones at once.
_Selecting elements_ of input documents is sometimes also called "pick fields"
or "include columns".
```yaml
expression: .[] |= pick(.meta, .data.temp)
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
Input Data
```json
[{
  "meta": {"id": "Hotzenplotz", "timestamp": 123456789},
  "data": {"temp": 42.42, "hum": 84}
}]
```
:::
:::{grid-item-card}
:margin: 0
:padding: 0
Output Data
```json
[{
  "meta": {"id": "Hotzenplotz", "timestamp": 123456789},
  "data": {"temp": 42.42}
}]
```
:::
:::{grid-item-card}
:margin: 0
:padding: 0
:columns: 12
Transformation definition
```{code-block} yaml
# Tikray collection-level transformation definition.
# Includes a Moksha/jq transformation rule for including elements.
# https://tikray.readthedocs.io/
---
meta:
  type: tikray-collection
  version: 1
pre:
  rules:
  - expression: .[] |= pick(.meta, .data.temp)
    type: jq
```
:::
::::
:::::
::::::

### Drop elements

::::::{card}
Drop object attributes by path, also multiple ones at once.
_Dropping elements_ of input documents is sometimes also called
"ignore fields" or "exclude columns".
```yaml
expression: .[] |= del(.meta.timestamp, .data.hum)
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
Input Data
```json
[{
  "meta": {"id": "Hotzenplotz", "timestamp": 123456789},
  "data": {"temp": 42.42, "hum": 84}
}]
```
:::
:::{grid-item-card}
:margin: 0
:padding: 0
Output Data
```json
[{
  "meta": {"id": "Hotzenplotz"},
  "data": {"temp": 42.42}
}]
```
:::
:::{grid-item-card}
:margin: 0
:padding: 0
:columns: 12
Transformation definition
```{code-block} yaml
# Tikray collection-level transformation definition.
# Includes a Moksha/jq transformation rule for excluding elements.
# https://tikray.readthedocs.io/
---
meta:
  type: tikray-collection
  version: 1
pre:
  rules:
  - expression: .[] |= del(.meta.timestamp, .data.hum)
    type: jq
```
:::
::::
:::::
::::::

::::::{card}
Drop attribute from all objects in array, where in some documents,
the array may not exist, or it might not be an array.
```yaml
expression: .[] |= del(.data.array[]?.hum)
```
:::::{dropdown} Example
::::{grid} 2
:gutter: 0
:margin: 0
:padding: 0

:::{grid-item-card}
:margin: 0
:padding: 0
Input Data
```json
[
  {"data": {"array": [
    {"temp": 42.42, "hum": 84},
    {"temp": 42.42, "hum": 84},
    {"temp": 42.42}
  ]}},
  {"data": {"array": 42}},
  {"data": {}},
  {"meta": {"version": 1}}
]
```
:::
:::{grid-item-card}
:margin: 0
:padding: 0
Output Data
```json
[
  {"data": {"array": [
    {"temp": 42.42},
    {"temp": 42.42},
    {"temp": 42.42}
  ]}},
  {"data": {"array": 42}},
  {"data": {}},
  {"meta": {"version": 1}}
]
```
:::
::::
:::::
::::::

::::::{card}
Drop array elements by index.
```yaml
expression: .[] |= del(.data.[1])
```
:::::{dropdown} Example
::::{grid} 2
:gutter: 0
:margin: 0
:padding: 0

:::{grid-item-card}
:margin: 0
:padding: 0
Input Data
```json
[{"data": [1, {"hum": 84}, 2]}]
```
:::
:::{grid-item-card}
:margin: 0
:padding: 0
Output Data
```json
[{"data": [1, 2]}]
```
:::
::::
:::::
::::::

### Rename elements
:::{todo}
Rename input elements, on any nesting level. 
:::

## Values

Transform actual field values, by applying converter functions, casting types,
and filtering on value content.

### Convert

Converting values is one of the most prominent tasks when transforming data.

#### Arithmetic

Arithmetic operations like `.data.temp /= 100` can easily apply value scaling
anywhere in the input document. See also [jq's arithmetic-update operator].
::::::{card}
Update value of deeply nested attribute if it exists.
```yaml
expression: .[] |= if .data.temp then .data.temp /= 100 end
```
:::::{dropdown} Example
::::{grid} 2
:gutter: 0
:margin: 0
:padding: 0

:::{grid-item-card}
:margin: 0
:padding: 0
Input Data
```json
[
  {"data": {"temp": 4242}},
  {"meta": {"version": 1}}
]
```
:::
:::{grid-item-card}
:margin: 0
:padding: 0
Output Data
```json
[
  {"data": {"temp": 42.42}},
  {"meta": {"version": 1}}
]
```
:::
::::
:::::
::::::

::::::{card}
Update value of deeply nested attribute within an array if it exists.
```yaml
expression: .[] |= if (.data | type == "array") and .data[].temp then .data[].temp /= 100 end
```
:::::{dropdown} Example
::::{grid} 2
:gutter: 0
:margin: 0
:padding: 0

:::{grid-item-card}
:margin: 0
:padding: 0
Input Data
```json
[
  {"data": [{"temp": 4242}]},
  {"data": [{"hum": 84}]},
  {"data": null},
  {"data": 42},
  {"meta": {"version": 1}}
]
```
:::
:::{grid-item-card}
:margin: 0
:padding: 0
Output Data
```json
[
  {"data": [{"temp": 42.42}]},
  {"data": [{"hum": 84}]},
  {"data": null},
  {"data": 42},
  {"meta": {"version": 1}}
]
```
:::
::::
:::::
::::::

#### Date / Time
:::{todo}
What can jq do with date / time / timestamp conversions? 
:::

### Combine
:::{todo}
Combine multiple fields into single ones. 
:::

### Filter
:::{todo}
Filter by values and value types. 
:::

### Type cast
:::{todo}
Cast types, i.e. substructure modifications, also see Tikray's stdlib. 
:::


[jq]: https://jqlang.org/
[jq manual]: https://jqlang.org/manual/
[jq playground]: https://play.jqlang.org/
[jq tutorial]: https://jqlang.org/tutorial/
[jq's arithmetic-update operator]: https://jqlang.org/manual/#arithmetic-update-assignment
[jq's built-in functions]: https://github.com/jqlang/jq/blob/master/src/builtin.jq
[jq's update operator]: https://jqlang.org/manual/#update-assignment
[Tikray's jqlang standard library]: https://github.com/panodata/tikray/blob/main/src/tikray/function.jq
