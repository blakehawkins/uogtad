# 4. Factories infer types on bare and specialised classes

Date: 2026-10-17
Status: accepted

## Context

ADR 0002 made factories take their type parameters through `cls`, keeping
covariance and explicit calls such as `Either[int, str].new(1)`. Mypy also
inferred bare calls correctly, but pyright resolved their class parameters to
`Unknown` before considering the value or assignment context. Basic pyright
accepted this, including in README-style assignments, so CI missed it.

## Decision

**Give `Either`, `Maybe` and `Validation` type parameters `Never` defaults.**
This represents the bare class without `Any` or `Unknown`. Defaults alone do
not solve inference: pyright would require `Never` as the factory argument.

**Put a bare-class overload before the specialised-class overload.** For
example, `Either.new` first accepts `cls: type[Either[Never, Never]]`, with
fresh method parameters for its value and result. Those parameters come from
the value and expected return type; any unprovided side defaults to `Never`.
The second overload keeps ADR 0002's signature for explicit specialisations.
The implementation accepts the covariant container class with `object`
parameters, covering both overloads without binding the argument type to
`cls`. The returned cases and runtime control flow stay the same.

The order matters. With the general overload first, mypy reports the bare
overload as unreachable, and pyright binds a bare call to the `Never`
parameters instead of inferring from the value.

**Check consumers in strict mode under both checkers.** `typing_tests/`
imports the public package and pins factory inference with `assert_type`,
including explicit specialisations, contextual assignments and downstream
composition. `just typecheck` and CI's existing pixi task run these checks.
The library's existing pyright mode stays unchanged; the consumer project's
strict configuration rejects partially unknown factory methods and results.

## Consequences

- `Either.new(1)` infers `Either[int, Never]` in both checkers, while
  `value: Either[int, str] = Either.new(1)` retains `Either[int, str]`.
- All seven public class factories use the same overload pattern. There are
  no casts, diagnostic suppressions or new `Any` annotations.
- Covariance and existing explicitly parameterised calls remain checked.
- Unparameterised container annotations now use `Never` defaults. Code that
  needs wider value or error types should spell those types explicitly.
- A union-based public API is unnecessary for this fix. Exhaustive pattern
  matching remains a separate design decision.
- Pyright still infers an `Unknown` error type when sequencing two
  success-only validations with `Never` error types. The same failure occurs
  with `Validation.sequence(Valid(1), Valid("a"))`, independently of these
  factories, and with `sequence_lazy`. This is a separate sequencing issue;
  the consumer checks pin the README's explicitly annotated error types.
