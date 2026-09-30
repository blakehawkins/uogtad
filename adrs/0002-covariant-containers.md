# 2. Every container is covariant, and says so

Date: 2026-09-30
Status: accepted

## Context

`Either`, `Maybe` and `Fallible` were invariant. An `Either[bool, ValueError]`
could not stand where an `Either[int, Exception]` was expected, and
`Either.flat_map` required its step to fail with exactly the same type as its
source. `Validation` made that cost visible: combining validations with
different error types, or chaining a step with its own, needed annotations or
rebuilt results.

The containers are immutable, so covariance is sound for them. Getting both
type checkers to accept it was the work. The class syntax, `class
Either[T, U]`, has no way to declare variance: it can only infer it. Both
checkers infer these containers as invariant, for reasons found by removing
one member at a time:

- **pyright** cannot infer covariance for a class that returns its own
  subclass, and `maybe_left()` returns a `Left`, `maybe_some()` a `Some` and
  `maybe_valid()` a `Valid`. The cases inherit those methods.
- **mypy** cannot infer it for a constructor that takes its types through
  `cls`, which the constructors below must. For `Fallible` it also cannot
  infer through `flat_map`'s widened result, `Fallible[V, E | G]`, while `E`
  has a bound.

Two shapes that looked likely are not causes: containers that return each
other, and state kept in private attributes.

## Decision

**Every container and every case is covariant, declared with `TypeVar`.**
`Either`, `Maybe`, `Validation` and `Fallible`, and `Left`, `Right`, `Some`,
`Empty`, `Valid` and `Invalid`, use `TypeVar(..., covariant=True)` and
`Generic[...]`. Each case lists its own value's type first and defaults the
other to `Never`, as before. Methods keep the class syntax for their own type
parameters. A comment above each declaration says why it cannot be inferred.

**Constructors take their types through `cls`.** A covariant type variable
cannot be a parameter, so `new` is `def new[V, W](cls: type[Either[V, W]],
value: V) -> Either[V, W]`, and likewise `right`, `empty`, `of_optional` and
`invalid`. `Either[int, str].new(1)`, and an annotated assignment, infer
exactly what they did before. Static constructors returning `Either[V, Never]`
were rejected: pyright narrows an annotated variable to the type assigned to
it, so later inference saw `Never`, and in places `Unknown`.

**Binds widen instead of requiring the same type.** `Either.flat_map` and
`flat_map_right`, `Fallible.flat_map` and `Validation.flat_map` accept a step
that brings its own type, and the result is the union, such as
`Fallible[V, E | G]`. `Validation.recover_with` may recover to another value
type. A step of the same type gives the same result as before.

**mypy's objection to the cases' fields is ignored.** From Python 3.13,
dataclasses generate `__replace__`, whose parameters are the fields, and mypy
refuses a covariant type there. A frozen dataclass's `__replace__` makes a new
object rather than changing the old one, so covariance stays sound. Each case's
field carries `# type: ignore[misc]`, and strict mypy reports an ignore that is
no longer needed, so each will be removed when mypy stops objecting.

## Consequences

- **It is not a breaking change.** Every test that existed before it passes
  unchanged, including those pinning inferred types. Each way of calling a
  constructor that was checked, on the bare class, on a specialised one, and
  into an annotated variable, infers the same type in both checkers as it did.
- **A test pins it.** `test_variance.py` assigns a narrower instance of each
  of the ten classes to a wider type, in both checkers.
- **The checkers will not catch a new mistake.** Their check of declared
  variance is shallow: it refuses a covariant type variable used directly as
  a parameter, but not one inside a parameter's type, such as the
  `Fallible[V, E]` a step once had to return. A new method must keep the
  class's type variables out of its parameters, and widen instead, as the
  binds do.
- **Fallible's covariance relies on its state.** Its result and captured
  exception types are set once, as it is made, and never reassigned.
- **A subclass outside `uogtad` that takes a class type variable as a
  parameter** would now be refused by both checkers. At runtime,
  `__type_params__` is now empty on every class, and `__parameters__` lists
  its type variables, marked covariant.
