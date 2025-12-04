(tools)=
# Tools

The list enumerates a few tools that are also valuable to wrangle (deeply)
nested JSON data.

- [jp]: A command line interface to JMESPath, an expression language for manipulating JSON.
- [jq]: A lightweight and flexible command-line JSON processor.
- [jsonpointer]: A commandline utility that can be used to resolve JSON pointers on JSON files.
- [rq]: A blazing fast JSONPath query engine written in Rust.

## Examples

Use `jq` to convert JSON file into JSONL / NDJSON file.
```shell
cat data.json | \
  jq --null-input --compact-output  --stream 'fromstream( inputs | (.[0] |= .[1:]) | select(. != [[]]) )' \
  > data.jsonl
```
-- https://stackoverflow.com/a/60961240
:::{todo}
Integrate into Tikray CLI and API.
:::


[jp]: https://github.com/jmespath/jp
[jq]: https://jqlang.github.io/jq/
[jsonpointer]: https://python-json-pointer.readthedocs.io/en/latest/commandline.html
[rq]: https://github.com/rsonquery/rsonpath
