# uoɥʇʎd

A functional control library for python in the same vein as io.vavr.control for java.

Provides three functional monads:

```python
class Either(Generic[T, U]):
    """A class that holds either a T or a U. In contrast to a python Union type, this is a concrete wrapper."""

class Maybe(Generic[T]):
    """
    A type-safe wrapper for a value or its absense.
    This is not the same thing as a `Union[T, None]` but rather a monad for computations over that form.
    Confusingly, in some languages this is called Optional -- but in python, Optional is an alias for Union[T, None].
    """

class Fallible(Generic[F]):
    """Represents the (un)successful computation of a Callable as either its return value or an Exception."""
```

Example usage:

```python
def raises():
    raise RuntimeError("tada")

tada: str | None = Fallible(raises).as_result().swap().map(lambda exc: cast(str, exc.args[0])).narrow().narrow()
assert tada == "tada"

def categorise(num: int) -> Either[Literal['A'], Literal['B']]:
    if num == 0:
        return Either.new('A')  # Either is left-biased, like Result[T, E].
    return Either.right('B')

just_a_lits: list[Literal['A']] = [
    cast(Literal['A'], y.narrow().narrow()) for y in [
        categorise(x) for x in [0, 1, 0, 2, 0, 3]
    ] if y.is_left()
]
assert just_a_lits == ["A", "A", "A"]

signal = None
inp = input("🐊")
possibly: Maybe[str] = Maybe(inp == "🛸").flat_map(lambda is_spaceship: Maybe("🐊") if is_spaceship else Maybe(None))
def signal_change(croc: str) -> None:
    nonlocal signal
    signal = f"💻 You got the croc! {croc}"
possibly.if_present(signal_change)
print(signal)
assert signal is not None
```


# Ops

Setup fresh clone:

```
conda env create -f .conda-env.yaml
conda activate uogtad
```

Persist env changes to env file:

```
./export_conda.yaml
```
