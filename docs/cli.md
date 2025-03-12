# Tikray CLI

## Install

```shell
uv tool install --upgrade --compile-bytecode 'tikray'
```

## Synopsis

Run data from input file `data.json` through transformation defined in
`transformation.yaml`.
```shell
tikray \
  --transformation=transformation.yaml \
  --input=data.json
```

## Usage

### Single collection

Process a single collection / file.
```shell
tikray -t transformation-collection.yaml -i eai-warehouse.json
```

### Multiple collections

Process multiple collections / files from a directory.
```shell
tikray -t examples/transformation-project.yaml -i examples/acme -o tmp/acme
```

## Example

`$ cat eai-warehouse.json`
```json
{
  "message-source": "system-3000",
  "message-type": "eai-warehouse",
  "records": [
    {"_id": "12", "meta": {"name": "foo", "location": "B"}, "data": {"value": "4242"}},
    null,
    {"_id": "34", "meta": {"name": "bar", "location": "BY"}, "data": {"value": -8401}},
    {"_id": "56", "meta": {"name": "baz", "location": "NI"}, "data": {"value": 2323}},
    {"_id": "78", "meta": {"name": "qux", "location": "NRW"}, "data": {"value": -580}},
    null,
    null
  ]
}
```

`$ cat transformation-collection.yaml`
```yaml
meta:
  version: 1
  type: tikray-collection
pre:
  rules:
  - expression: records[?not_null(meta.location) && !starts_with(meta.location, 'N')]
    type: jmes
bucket:
  names:
    rules:
    - new: id
      old: _id
  values:
    rules:
    - pointer: /id
      transformer: builtins.int
    - pointer: /data/value
      transformer: builtins.float
post:
  rules:
  - expression: .[] |= (.data.value /= 100)
    type: jq
```

```shell
tikray -t transformation-collection.yaml -i eai-warehouse.json
```
```json
[
  {"id": 12, "meta": {"name": "foo", "location": "B"}, "data": {"value": 42.42}},
  {"id": 34, "meta": {"name": "bar", "location": "BY"}, "data": {"value": -84.01}}
]
```
