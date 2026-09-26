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

## Comparison with other libraries

[`returns`](https://returns.readthedocs.io/) is a broad collection of typed
functional abstractions, including IO-aware and asynchronous containers,
composable point-free helpers, and framework integrations. Choose it when an
application benefits from that larger functional-programming ecosystem.

For like-for-like concepts, `returns` models success with the right-biased
`Success` case of `Result`, while `uogtad.Either` maps and flat-maps its
left-hand case. Its optional container uses `Some` and a singleton `Nothing`;
`uogtad.Maybe` instead uses `Some` and constructible `Empty` variants. Both
offer explicit conversion from `T | None`, but `uogtad` additionally makes the
distinction between `Maybe.new(None)` (a present `Some(None)`) and
`Maybe.of_optional(None)` (an `Empty`) visible in its constructors. `Fallible`
is the compact counterpart to converting exception-raising functions into a
`returns` `Result`, without adding IO or asynchronous container layers.

[`Expression`](https://expression.readthedocs.io/) is inspired by F# and
provides discriminated unions, computation expressions, immutable collections,
and functional utilities in addition to `Option` and `Result`. Choose it when
those F#-style abstractions should shape more of the application.

At the container level, Expression names its result variants `Ok` and `Error`
and its optional variants `Some` and `Nothing`; `uogtad` uses `Left` and
`Right`, and `Some` and `Empty`. Expression's `Result` maps the `Ok` case,
whereas `uogtad.Either` is deliberately left-biased. The libraries share core
operations such as mapping, binding/flat-mapping, defaults, optional
conversion, and structural matching, but `uogtad` keeps only a method-oriented
surface and adds `Fallible` for immediately capturing an ordinary Python
exception.

`uogtad` deliberately has a smaller scope: `Either`, `Maybe`, and `Fallible`,
with concrete variants that work naturally with Python pattern matching and
strict type checking. Choose it when those control containers are sufficient
and a compact API is preferable.
