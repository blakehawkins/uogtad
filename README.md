# uoɥʇʎd

[![CI](https://github.com/blakehawkins/uogtad/actions/workflows/ci.yml/badge.svg)](https://github.com/blakehawkins/uogtad/actions/workflows/ci.yml)
[![Python 3.15](https://img.shields.io/badge/python-3.15-blue.svg)](https://docs.python.org/3.15/)
[![mypy: strict](https://img.shields.io/badge/mypy-strict-blue.svg)](https://mypy-lang.org/)
[![Pyright](https://img.shields.io/badge/pyright-checked-blue.svg)](https://github.com/microsoft/pyright)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](https://opensource.org/license/mit)

A functional control library for python in the same vein as io.vavr.control for java.

Provides four immutable, typed control containers:

```python
Either.new(value)       # Left(value)
Either.right(error)     # Right(error)
Maybe.new(value)        # Some(value), even when value is None
Maybe.empty()           # Empty()
Maybe.of_optional(value) # Empty() for None, otherwise Some(value)
Fallible(computation)   # captures Exception, but not KeyboardInterrupt/SystemExit
Fallible(computation, ValueError)  # captures only ValueError (and subclasses)
Validation.new(value)   # Valid(value)
Validation.invalid(error) # Invalid((error,)), whose errors combine with others'
```

Example usage:

```python
from typing import Literal

from uogtad import Either, Fallible

def raises() -> str:
    raise RuntimeError("tada")

tada = Fallible(raises).as_result().swap().map(lambda exc: str(exc.args[0])).narrow().narrow()
assert tada == "tada"

# Unexpected exceptions remain bugs instead of becoming values. A tuple works
# just like an ``except`` clause when several exception types are expected.
parsed = Fallible(lambda: int("not a number"), (ValueError, RuntimeError))
if failure := parsed.maybe_exception():
    # ``failure.value`` is statically narrowed to ValueError | RuntimeError.
    assert isinstance(failure.value, ValueError)

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

`Either` stops at its first error. `Validation` is for checks that should all
run: `Validation.sequence` combines independent validations into a tuple of
their values, or, if any is invalid, every error of all of them, in order.

```python
from uogtad import Invalid, Valid, Validation

def check(name: str, ok: bool) -> Validation[str, str]:
    return Validation.new(name) if ok else Validation.invalid(f"{name} failed")

assert Validation.sequence(check("a", True), check("b", False), check("c", False)) == Invalid(("b failed", "c failed"))

# Up to six validations keep each one's type, and their errors' types combine.
# More are all still combined, but a type checker sees only a common type.
count: Validation[int, ValueError] = Validation.new(1)
name: Validation[str, KeyError] = Validation.new("a")
both = Validation.sequence(count, name)  # Validation[tuple[int, str], ValueError | KeyError]
assert both == Valid((1, "a"))

# `sequence_lazy` takes the functions that make them instead, and can run
# them together on a concurrent.futures executor.
assert Validation.sequence_lazy(lambda: count, lambda: name) == Valid((1, "a"))
```

Every container is immutable, and so covariant: a `Validation[bool, ValueError]`
can stand where a `Validation[int, Exception]` is expected.

A step that needs a validation's value is chained with `flat_map`, which is
bind: with no value to give the step, it stops at the first invalid
validation. `map` transforms a valid value. `Fallible.as_validation()` and
`Either.as_validation()` turn a captured exception or a right value into a
validation's one error.


# Ops

Install the latest release from PyPI (Python 3.15 or newer):

```shell
python -m pip install uogtad
```

Install the current `master` branch directly from GitHub (Python 3.15 or newer)
with pip:

```shell
python -m pip install "uogtad @ git+https://github.com/blakehawkins/uogtad.git@master"
```

Or add the same PyPI-compatible Git dependency to a Pixi project:

```shell
pixi add --pypi "uogtad @ git+https://github.com/blakehawkins/uogtad.git@master"
```

### Development

Install [pixi](https://pixi.sh) and [just](https://just.systems). Every command
is a `just` recipe, and `just --list` shows them all. The first one installs
the environment, including uogtad itself, editable:

```shell
just validate   # the tests, then both type checkers
just test       # the tests alone; arguments go to pytest
just typecheck  # mypy (strict) and pyright
just package    # build the distributions and check them with twine
```

### Releases

Releases use [Release Please](https://github.com/googleapis/release-please#readme)
and [PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/), so no
GitHub repository secrets are required.

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

`uogtad` deliberately has a smaller scope: `Either`, `Maybe`, `Fallible`, and
`Validation`, with operations exposed directly as methods. It intentionally avoids
decorator-driven control flow, free-function combinators, and a pipeline DSL.
Choose it when ordinary method chaining, Python pattern matching, and a compact
API are preferable.
