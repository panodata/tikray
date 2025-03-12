# Tikray

[![Tests](https://github.com/panodata/tikray/actions/workflows/tests.yml/badge.svg)](https://github.com/panodata/tikray/actions/workflows/tests.yml)
[![Coverage](https://codecov.io/gh/panodata/tikray/branch/main/graph/badge.svg)](https://app.codecov.io/gh/panodata/tikray)
[![Build status (documentation)](https://readthedocs.org/projects/tikray/badge/)](https://tikray.readthedocs.io/)
[![License](https://img.shields.io/pypi/l/tikray.svg)](https://pypi.org/project/tikray/)

[![PyPI Version](https://img.shields.io/pypi/v/tikray.svg)](https://pypi.org/project/tikray/)
[![Python Version](https://img.shields.io/pypi/pyversions/tikray.svg)](https://pypi.org/project/tikray/)
[![PyPI Downloads](https://pepy.tech/badge/tikray/month)](https://pepy.tech/project/tikray/)
[![Status](https://img.shields.io/pypi/status/tikray.svg)](https://pypi.org/project/tikray/)

## About

Tikray is a generic and compact **transformation engine** written in Python, for data
decoding, encoding, conversion, translation, transformation, and cleansing purposes,
to be used as a pipeline element for data pre- or post-processing, or as a standalone
converter program.

## Details

A data model and implementation for a compact transformation engine based on
[JMESPath], [jq], [JSON Pointer] (RFC 6901), [transon], and [DWIM].

The reference implementation is written in [Python], using [attrs] and [cattrs].
The design, conventions, and definitions also encourage implementations
in other programming languages.

## Installation

The package is available from [PyPI] at [tikray].
To install the most recent version, invoke:
```shell
uv pip install --upgrade 'tikray'
```

## Usage

In order to learn how to use the library, please visit the [documentation],
and explore the source code or its [examples].


## Project Information

### Acknowledgements
Kudos to the authors of all the many software components this library is
vendoring and building upon.

### Similar Projects
See [research and development notes],
specifically [an introduction and overview about Singer].

### Contributing
The `tikray` package is an open source project, and is
[managed on GitHub]. The project is still in its infancy, and
we appreciate contributions of any kind.

### Etymology
Tikray means "transform" in the [Quechua language].
A previous version used the name `zyp`,
with kudos to [Kris Zyp] for conceiving [JSON Pointer].

### License
The project uses the LGPLv3 license for the whole ensemble. However, individual
portions of the code base are vendored from other Python packages, where
deviating licenses may apply. Please check for detailed license information
within the header sections of relevant files.



[An introduction and overview about Singer]: https://github.com/daq-tools/lorrystream/blob/main/doc/singer/intro.md
[documentation]: https://tikray.readthedocs.io/
[examples]: https://tikray.readthedocs.io/examples.html
[Kris Zyp]: https://github.com/kriszyp
[tikray]: https://pypi.org/project/tikray/
[Quechua language]: https://en.wikipedia.org/wiki/Quechua_language
[managed on GitHub]: https://github.com/panodata/tikray
[PyPI]: https://pypi.org/
[research and development notes]: https://tikray.readthedocs.io/research.html

[attrs]: https://www.attrs.org/
[cattrs]: https://catt.rs/
[DWIM]: https://en.wikipedia.org/wiki/DWIM
[jq]: https://jqlang.org/
[jsonpointer]: https://python-json-pointer.readthedocs.io/en/latest/commandline.html
[jqlang]: https://jqlang.github.io/jq/manual/
[JMESPath]: https://jmespath.org/
[JSON Pointer]: https://datatracker.ietf.org/doc/html/rfc6901
[Python]: https://en.wikipedia.org/wiki/Python_(programming_language)
[transon]: https://transon-org.github.io/
