# 1. What Validation's operations are called

Date: 2026-09-30
Status: accepted

## Context

`Validation` joins `Either`, `Maybe` and `Fallible` for checks that should all
run: where `Either` stops at its first error, validations combine and keep
every error. Four libraries already name this kind of container's operations,
and none of them agree:

| Concept | uogtad | vavr | frunk | Haskell `validation` | Cats |
|---|---|---|---|---|---|
| Cases | `Valid`, `Invalid` | valid, invalid | `Ok`, `Err` | `Success`, `Failure` | `Valid`, `Invalid` |
| Combine independent validations | `sequence` | `combine(...).ap(f)`, `sequence` | `+` | `<*>`, `sequenceA` | `mapN`, `tupled`, `sequence` |
| A step that needs the value | `flat_map` | `flatMap` | none | `bindValidation` | `andThen` |
| Transform the errors | `map_invalid` | `mapError` | none | `first` | `leftMap` |
| Recover from the errors | `recover_with` | `orElse`, given another validation | none | none | `handleErrorWith` |

`uogtad` does not have to mirror any of them. Its own containers already fix
some names: `new`, `map`, `flat_map`, `or_else` and `narrow` mean the same
thing on `Either`, `Maybe` and `Fallible`.

## Decision

**Combining is `sequence`, and `sequence_lazy` takes the functions instead.**
`Validation.sequence(*validations)` gives a tuple of every value, or every
error of all of them, in order. `Validation.sequence_lazy(*makers,
executor=None)` makes nothing until it is called, and runs the functions in
order, or together on a `concurrent.futures` executor. `sequence` is what Cats
and vavr call combining many validations of one type, and Haskell
`sequenceA`; ours also keeps each type of a fixed set, which they spell
`mapN`, `combine` or `<*>`.

Up to six validations keep each one's type in the tuple, as typeshed's stubs
for `asyncio.gather` do. Python's type system cannot name one
type per argument for any number of arguments: that needs a type mapped over a
variadic list, which PEP 646 left for later. Beyond six, validations are all
still combined, and a type checker sees a type they have in common.

**A dependent step is `flat_map`, with a warning.** It is bind: a step that
needs the value cannot run without it, so a chain of steps stops at the first
invalid validation. Haskell names it `bindValidation`, and Cats `andThen`, so
that nobody expects it to keep every error as combining does. `uogtad` keeps
`flat_map`, the name its other containers use, and its docstring warns that it
does not accumulate.

**`map` stays.** It transforms a valid value and leaves an invalid one as it
is. It cannot fail, switch tracks or combine anything, so it cannot be
confused with accumulation, and it behaves as it does on every container.

**Recovering is `recover_with`.** It receives every error at once and returns
another validation. `or_else` is taken: on every container it means the value,
or a fallback. `recover_with` follows `Try.recoverWith` in Scala and vavr.
Transforming each error is `map_invalid`.

**The constructors stay `new` and `invalid`.** Every peer pairs "valid" with
"invalid", but `new` is what `Either` and `Maybe` call theirs. Renaming it, or
`or_else` and `narrow`, would be a breaking change, which is not worth making
on its own; they are reconsidered only alongside another one.

**Rejected:**

- **`+`, and the built-in `sum()`.** Adding valid values requires them to be
  addable, and `sum`'s signature cannot follow a type that changes as values
  are appended: both checkers infer a union of the item and start types.
- **Chaining `zip` and `also` over a growing tuple.** `tuple[*Ts, U]` gives
  exact types for any number of validations, added one at a time. It was set
  aside for `sequence`, which takes them all in one call and has a lazy
  counterpart that can run them together.
- **Deciding between pairing and appending by looking at the value.** In
  generic code the checker and the runtime disagree: a `Validation[T, str]`
  combined with another is typed as a pair, but a tuple-valued `T` is
  flattened at runtime.

## Consequences

- Validation reads like the rest of `uogtad`, at the cost of `flat_map`
  needing its warning, which a Haskell or Cats name would not.
- The fixed-set overloads end at six, and adding more is a matter of more
  overloads.
