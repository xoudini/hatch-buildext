# hatch-buildext

[![PyPI - Version](https://img.shields.io/pypi/v/hatch-buildext.svg)](https://pypi.org/project/hatch-buildext)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/hatch-buildext.svg)](https://pypi.org/project/hatch-buildext)
[![Checks & Tests](https://github.com/xoudini/hatch-buildext/actions/workflows/test.yml/badge.svg)](https://github.com/xoudini/hatch-buildext/actions)

---

## Table of Contents

- [Usage](#usage)
  - [Example](#example)
  - [Resolvers](#resolvers)
- [License](#license)

## Usage

The only key currently recognised is `extensions`.
This should be a map of key-value pairs mapping the extension name to a [resolver](#resolvers).

```toml
# pyproject.toml
[tool.hatch.build.targets.wheel.hooks.buildext]
dependencies = ["hatch-buildext"]

[tool.hatch.build.targets.wheel.hooks.buildext.extensions]
libsome = "path.to.resolver"
libother =  "path.to.another"
```

### Example

For instance, if using [src layout][src-layout],
the directory structure could look as follows:

```console
.
├── LICENSE.txt
├── README.md
├── pyproject.toml
├── src
│   ├── resolvers
│   │   ├── lib_a.py
│   │   └── lib_b.py
│   ├── liba
│   │   ├── foo.h
│   │   └── foo.c
│   ├── libb
│   │   ├── bar.h
│   │   └── bar.c
│   └── mypackage
│       ├── __about__.py
│       ├── __init__.py
│       ├── ...
│       └── core.py
└── tests
    ├── __init__.py
    ├── conftest.py
    ├── ...
    └── test_core.py
```

Then, if that you want to include both libraries as module extensions in `mypackage`,
the `extensions` configuration would look as follows:

```toml
[tool.hatch.build.targets.wheel.hooks.buildext.extensions]
"mypackage.lib_a" = "src.resolvers.lib_a"
"mypackage.lib_b" =  "src.resolvers.lib_b"
```

> [!WARNING]
> The configuration may change at any time until this package is stable.

### Resolvers

Resolvers may implement or omit any part of the interface [here](./src/hatch_buildext/resolver.py).
Each function will be passed the root of of the project directory while building,
in order to make it easier to provide paths to build requirements in the project tree.

The meaning of these functions are identical to those in the [setuptools Extension API][setuptools].

> [!WARNING]
> The interface may change at any time until this package is stable.

## License

`hatch-buildext` is distributed under the terms of the [Apache-2.0][license] license.

<!-- MARK: links -->

[src-layout]: https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout
[setuptools]: https://setuptools.pypa.io/en/latest/userguide/ext_modules.html
[license]: https://spdx.org/licenses/Apache-2.0.html
