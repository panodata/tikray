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

Process a single resource (collection, file) using a Tikray collection transformation.
```shell
tikray -t transformation-collection.yaml -i eai-warehouse.json
```

### Multiple collections

Process multiple resources (collections, files) from a directory.
The Tikray project file enumerates multiple transformation rules per resource.
```shell
tikray -t examples/transformation-project.yaml -i examples/acme -o tmp/acme
```

If you are using a Tikray project file, but would like to only invoke a
single-resource transformation on it, you need to explicitly specify the
resource address using `--address`/`-a`, so the engine will only select
this particular collection.
```shell
tikray -t examples/transformation-project.yaml -i examples/acme/conversation.json -a acme.conversation
```

### JSONL support

Tikray supports reading and writing the JSONL/NDJSON format, i.e. newline-
delimited JSON. Tikray will automatically use this mode if it receives
input files suffixed with `.jsonl` or `.ndjson`, or if you explicitly
toggle the mode per `--jsonl` option flag.
```shell
tikray -t transformation.yaml -i input.jsonl
```
```shell
tikray -t transformation.yaml -i input.json -a acme.conversation --jsonl -o output.jsonl
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
