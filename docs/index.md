# Tikray Transformations

## About

A data model and implementation for a compact transformation engine based on
[JMESPath], [jq], [JSON Pointer] (RFC 6901), [transon], and [DWIM].

The reference implementation is written in [Python], using [attrs] and [cattrs].
The design, conventions, and definitions also encourage implementations
in other programming languages.

```{include} readme.md
:start-line: 3
:end-line: 11
```

## Features

:Conciseness:
    Define a multistep data refinement process with as little code as possible.
:Precision:
    When filtering and manipulating deeply nested documents, you want to exactly
    address specific elements and substructures.
:Polyglot:
    The toolbox includes different kinds of tools, to always have the
    right one at hand. The venerable jq language is always on your fingertips,
    while people accustomed to JMESPath expressions as employed by AWS CLI's
    \\-\\-query parameter can also use it. On top of that, transformation
    steps can also be written in Python.
:Flexibility:
    The library can be used both within frameworks, applications, and ad hoc
    pipelines equally well. It does not depend on any infrastructure services,
    and can be used together with any other ETL or pipeline framework.
:Interoperability:
    Transformation recipe definitions are represented by a concise data model,
    which can be marshalled to/from text-only representations like JSON or YAML,
    in order to
    a) encourage implementations in other programming languages, and
    b) be transferred, processed and stored by third party systems.
:Performance:
    Depending on how many transformation rules are written in pure Python vs.
    more efficient processors like jqlang or other compiled transformation
    languages, it may be slower or faster. When applicable, hot spots of the
    library may gradually be rewritten in Rust if that topic becomes an issue.
:Immediate:
    Other ETL frameworks and concepts often need to first land your data in the
    target system before applying subsequent transformations. Tikray is working
    directly within the data pipeline, before data is inserted into the target
    system.
:Human:
    Tikray provides capabilities to imperatively filter and reshape data structures
    in an iterative authoring process, based on deterministic procedures building
    upon each other. When it comes to ad hoc or automated data conversion tasks,
    it puts you into the driver's seat, and encourages sharing and reuse of
    transformation recipes.

## Design

:Data Model:
    The data model of Tikray is hierarchical: A Tikray project includes definitions for
    multiple Tikray collections, whose includes definitions for possibly multiple sets
    of transformation rules of different kinds, for example multiple items of
    type `BucketTransformation` or `MokshaTransformation`.

:Components and Rules:
    Those transformation components offer different kinds of features, mostly by
    building upon well-known data transformation standards and processors like
    JSON Pointer, `jq`, and friends. The components are configured using rules.

:Phases and Process:
    The transformation process includes multiple phases that are
    defined by labels like `pre`, `bucket`, `post`, `treatment`, in that order.
    Each phase can include multiple rules of different kinds.

## Usage

```{toctree}
:maxdepth: 2

cli
```

## Synopsis

::::{tab-set}

:::{tab-item} tikray-project
```{code-block} yaml
:caption: A definition for a Tikray project in YAML format.
meta:
  type: tikray-project
  version: 1
collections:
- address:
    container: testdrive-db
    name: foobar-collection
  schema:
    rules:
    - pointer: /some_date
      type: DATETIME
    - pointer: /another_date
      type: DATETIME
  bucket:
    values:
      rules:
      - pointer: /some_date
        transformer: to_unixtime
      - pointer: /another_date
        transformer: to_unixtime
```

:::

:::{tab-item} tikray-collection
```{code-block} yaml
:caption: A definition for a Tikray collection in YAML format.

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
:::

::::


## Example Gallery

In order to learn how to use Tikray, please explore the hands-on example gallery.
```{toctree}
:maxdepth: 2

Examples <examples>
```
You are also welcome to explore and inspect the software test cases to get further
inspirations that might not have been reflected on the documentation yet.

## Tools

- [jp]: A command line interface to JMESPath, an expression language for manipulating JSON.
- [jq]: A lightweight and flexible command-line JSON processor.
- [jsonpointer]: A commandline utility that can be used to resolve JSON pointers on JSON files.

## Prior Art

See {ref}`research and development notes <research>`,
specifically [an introduction and overview about Singer].

## Etymology

Tikray means "transform" in the [Quechua language].
A previous version used the name `zyp`,
with kudos to [Kris Zyp] for conceiving [JSON Pointer].

```{toctree}
:maxdepth: 1
:hidden:

Changelog <changes>
Research <research>
Backlog <backlog>
```



[An introduction and overview about Singer]: https://github.com/daq-tools/lorrystream/blob/main/doc/singer/intro.md
[attrs]: https://www.attrs.org/
[cattrs]: https://catt.rs/
[DWIM]: https://en.wikipedia.org/wiki/DWIM
[Kris Zyp]: https://github.com/kriszyp
[Quechua language]: https://en.wikipedia.org/wiki/Quechua_language
[jp]: https://github.com/jmespath/jp
[jq]: https://jqlang.github.io/jq/
[jsonpointer]: https://python-json-pointer.readthedocs.io/en/latest/commandline.html
[jqlang]: https://jqlang.github.io/jq/manual/
[JMESPath]: https://jmespath.org/
[JSON Pointer]: https://datatracker.ietf.org/doc/html/rfc6901
[Python]: https://en.wikipedia.org/wiki/Python_(programming_language)
[transon]: https://transon-org.github.io/
