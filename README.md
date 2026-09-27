# uoɥʇʎd

[![CI](https://github.com/blakehawkins/uogtad/actions/workflows/ci.yml/badge.svg)](https://github.com/blakehawkins/uogtad/actions/workflows/ci.yml)
[![Python 3.15](https://img.shields.io/badge/python-3.15-blue.svg)](https://docs.python.org/3.15/)
[![mypy: strict](https://img.shields.io/badge/mypy-strict-blue.svg)](https://mypy-lang.org/)
[![Pyright](https://img.shields.io/badge/pyright-checked-blue.svg)](https://github.com/microsoft/pyright)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/license/mit)

A functional control library for python in the same vein as io.vavr.control for java.

Provides three immutable, typed control containers:

```python
Either.new(value)       # Left(value)
Either.right(error)     # Right(error)
Maybe.new(value)        # Some(value), even when value is None
Maybe.empty()           # Empty()
Maybe.of_optional(value) # Empty() for None, otherwise Some(value)
Fallible(computation)   # captures Exception, but not KeyboardInterrupt/SystemExit
```

Example usage:

```python
from typing import Literal

from uogtad import Either, Fallible

def raises() -> str:
    raise RuntimeError("tada")

tada = Fallible(raises).as_result().swap().map(lambda exc: str(exc.args[0])).narrow().narrow()
assert tada == "tada"

def categorise(num: int) -> Either[Literal['A'], Literal['B']]:
    if num == 0:
        return Either.new('A')  # Either is left-biased, like Result[T, E].
    return Either.right('B')

results = list(map(categorise, [0, 1, 0, 2, 0, 3]))
assert [result.is_left() for result in results] == [True, False, True, False, True, False]

result = categorise(0)
if left := result.maybe_left():
    # Static checkers narrow `left` to Left[Literal['A']].
    assert left.value == "A"

```


# Ops

Install the current `master` branch directly from GitHub (Python 3.15 or newer)
with pip:

```shell
python -m pip install "uogtad @ git+https://github.com/blakehawkins/uogtad.git@master"
```

Or add the same PyPI-compatible Git dependency to a Pixi project:

```shell
pixi add --pypi "uogtad @ git+https://github.com/blakehawkins/uogtad.git@master"
```

Run the test suite:

```shell
pixi run python -m pytest
```

Build and validate the PyPI distributions:

```shell
pixi run package
```

## Comparison with other libraries

[`returns`](https://returns.readthedocs.io/) is a broad collection of typed
functional abstractions, including IO-aware and asynchronous containers. Its
decorators, point-free helpers, and `flow` utilities encourage building
annotated function pipelines. Choose it when an application benefits from that
larger functional-programming ecosystem and composition style.

[`Expression`](https://expression.readthedocs.io/) is inspired by F# and
provides discriminated unions, computation expressions, immutable collections,
and functional utilities in addition to `Option` and `Result`. Its decorators,
free functions, and `pipe` helpers support an F#-style pipeline-oriented
application design. Choose it when those abstractions should shape more of the
application.

`uogtad` deliberately has a smaller scope: `Either`, `Maybe`, and `Fallible`,
with operations exposed directly as methods. It intentionally avoids
decorator-driven control flow, free-function combinators, and a pipeline DSL.
Choose it when ordinary method chaining, Python pattern matching, and a compact
API are preferable.
