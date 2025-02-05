# Loko

[![Tests](https://github.com/panodata/loko/actions/workflows/tests.yml/badge.svg)](https://github.com/panodata/loko/actions/workflows/tests.yml)
[![Coverage](https://codecov.io/gh/panodata/loko/branch/main/graph/badge.svg)](https://app.codecov.io/gh/panodata/loko)
[![Build status (documentation)](https://readthedocs.org/projects/loko/badge/)](https://loko.readthedocs.io/)
[![License](https://img.shields.io/pypi/l/loko.svg)](https://pypi.org/project/loko/)

[![PyPI Version](https://img.shields.io/pypi/v/loko.svg)](https://pypi.org/project/loko/)
[![Python Version](https://img.shields.io/pypi/pyversions/loko.svg)](https://pypi.org/project/loko/)
[![PyPI Downloads](https://pepy.tech/badge/loko/month)](https://pepy.tech/project/loko/)
[![Status](https://img.shields.io/pypi/status/loko.svg)](https://pypi.org/project/loko/)

## About

Loko is a generic and compact **transformation engine** written in Python, for data
decoding, encoding, conversion, translation, transformation, and cleansing purposes,
to be used as a pipeline element for data pre- and/or post-processing.

## Details

A data model and implementation for a compact transformation engine written
in [Python], based on [JSON Pointer] (RFC 6901), [JMESPath], and [transon],
implemented using [attrs] and [cattrs].

## Installation

The package is available from [PyPI] at [loko].
To install the most recent version, invoke:
```shell
uv pip install --upgrade 'loko'
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
The `loko` package is an open source project, and is
[managed on GitHub]. The project is still in its infancy, and
we appreciate contributions of any kind.

### Etymology
Loko means "transform" in the [Luo language]. 
A previous version used the name `zyp`,
with kudos to [Kris Zyp] for conceiving [JSON Pointer].

### License
The project uses the LGPLv3 license for the whole ensemble. However, individual
portions of the code base are vendored from other Python packages, where
deviating licenses may apply. Please check for detailed license information
within the header sections of relevant files.



[An introduction and overview about Singer]: https://github.com/daq-tools/lorrystream/blob/main/doc/singer/intro.md
[documentation]: https://loko.readthedocs.io/
[examples]: https://loko.readthedocs.io/examples.html
[Kris Zyp]: https://github.com/kriszyp
[loko]: https://pypi.org/project/loko/
[Luo language]: https://en.wikipedia.org/wiki/Luo_language
[managed on GitHub]: https://github.com/panodata/loko
[PyPI]: https://pypi.org/
[research and development notes]: https://loko.readthedocs.io/research.html

[attrs]: https://www.attrs.org/
[cattrs]: https://catt.rs/
[DWIM]: https://en.wikipedia.org/wiki/DWIM
[jp]: https://github.com/jmespath/jp
[jq]: https://jqlang.github.io/jq/
[jsonpointer]: https://python-json-pointer.readthedocs.io/en/latest/commandline.html
[jqlang]: https://jqlang.github.io/jq/manual/
[JMESPath]: https://jmespath.org/
[JSON Pointer]: https://datatracker.ietf.org/doc/html/rfc6901
[Python]: https://en.wikipedia.org/wiki/Python_(programming_language)
[transon]: https://transon-org.github.io/
