# uoɥʇʎd

A functional control library for python in the same vein as io.vavr.control for java.

Provides three immutable, typed control containers. `Either` and `Maybe` use
distinct runtime variants, so falsy values (including `None`) remain real values
and static type checkers can distinguish each case:

```python
Either.new(value)       # Left(value)
Either.right(error)     # Right(error)
Maybe(value)            # Some(value), even when value is None
Maybe.empty()           # Empty()
Fallible(computation)   # captures Exception, but not KeyboardInterrupt/SystemExit
```

Example usage:

```python
from typing import Literal

from uogtad import Either, Fallible, Left, Maybe

def raises() -> str:
    raise RuntimeError("tada")

tada = Fallible(raises).as_result().swap().map(lambda exc: str(exc.args[0])).narrow().narrow()
assert tada == "tada"

def categorise(num: int) -> Either[Literal['A'], Literal['B']]:
    if num == 0:
        return Either.new('A')  # Either is left-biased, like Result[T, E].
    return Either.right('B')

just_a_lits = [
    result.value
    for result in map(categorise, [0, 1, 0, 2, 0, 3])
    if isinstance(result, Left)
]
assert just_a_lits == ["A", "A", "A"]

def find_croc(inp: str) -> str | None:
    possibly = Maybe(inp == "🛸").flat_map(
        lambda is_spaceship: Maybe("🐊") if is_spaceship else Maybe.empty()
    )
    return possibly.map(lambda croc: f"💻 You got the croc! {croc}").narrow()

assert find_croc("🛸") == "💻 You got the croc! 🐊"
```


# Ops

Install a fresh clone (Python 3.11 or newer):

```
python -m venv .venv
. .venv/bin/activate
python -m pip install -e .
```

Run the test suite:

```
python -m pytest
```
