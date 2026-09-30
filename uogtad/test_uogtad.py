from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from typing import Literal, Never, assert_type

import pytest

from uogtad import Either, Empty, Fallible, Invalid, Left, Maybe, Right, Some, Valid, Validation


@pytest.mark.parametrize("value", [0, "", [], False, None])
def test_either_preserves_falsy_left_values(value: object) -> None:
    result: Either[object, Never] = Either.new(value)
    assert result.map(lambda item: (item, "mapped")) == Left((value, "mapped"))
    assert result.narrow() == Some(value)


def test_either_cases_support_equality_repr_and_matching() -> None:
    assert Either.new(1) == Either.new(1)
    assert repr(Either.right("error")) == "Right(value='error')"
    match Either.new(None):
        case Left(value):
            assert value is None
        case Right():  # pragma: no cover - protects exhaustiveness at runtime
            pytest.fail("unexpected right")


def test_either_operations() -> None:
    result: Either[int, str] = Either.new(1)
    assert result.map(lambda value: value + 1) == Left(2)
    assert result.flat_map(lambda value: Either.new(value + 2)) == Left(3)
    assert Either.right("bad").map_right(str.upper) == Right("BAD")
    assert Either.right("bad").swap() == Left("bad")
    assert Either.right("bad").context("failed").is_right()


def test_either_variant_guards_narrow_to_concrete_cases() -> None:
    result: Either[int, str] = Either.new(1)
    if left := result.maybe_left():
        assert left.value + 1 == 2
    else:  # pragma: no cover - protects type narrowing at runtime
        pytest.fail("expected left")

    assert result.maybe_right() is None


@pytest.mark.parametrize("value", [0, "", [], False, None])
def test_maybe_preserves_present_falsy_values(value: object) -> None:
    maybe = Maybe(value)
    assert maybe.is_present()
    assert maybe.or_else("fallback") == value
    assert maybe.or_else_get(lambda: "fallback") == value
    assert maybe.filter(lambda _: True) == Some(value)
    assert maybe.map(lambda item: (item, "mapped")) == Some((value, "mapped"))


def test_empty_maybe() -> None:
    empty: Maybe[int] = Maybe.empty()
    assert empty == Empty()
    assert empty.or_else(99) == 99
    assert empty.flat_map(lambda value: Some(value + 1)) == Empty()
    assert empty.maybe_some() is None


@pytest.mark.parametrize("value", [0, "", [], False])
def test_maybe_of_optional_preserves_non_none_values(value: object) -> None:
    assert Maybe.of_optional(value) == Some(value)


def test_maybe_of_optional_converts_none_to_empty() -> None:
    assert Maybe.of_optional(None) == Empty()


def test_maybe_guard_narrows_to_some() -> None:
    if some := Maybe(0).maybe_some():
        assert some.value == 0
    else:  # pragma: no cover - protects type narrowing at runtime
        pytest.fail("expected some")


@pytest.mark.parametrize("value", [0, "", [], False, None])
def test_fallible_preserves_falsy_successes(value: object) -> None:
    result = Fallible(lambda: value)
    assert result.is_success()
    assert result.as_result() == Left(value)
    assert result.or_else(lambda _: "fallback") == value


def test_fallible_defaults_to_capturing_exception() -> None:
    result = Fallible(lambda: 1)
    assert_type(result, Fallible[int, Exception])
    assert_type(result.maybe_exception(), Right[Exception, int] | None)


def test_fallible_map_and_flat_map_capture_callback_errors() -> None:
    mapped = Fallible(lambda: 1).map(lambda _: 1 / 0)
    assert mapped.is_exception()
    mapped_result = mapped.as_result()
    assert isinstance(mapped_result, Right)
    assert isinstance(mapped_result.value, ZeroDivisionError)

    def fail(_: int) -> Fallible[str]:
        raise ValueError("bad callback")

    flat_mapped_result = Fallible(lambda: 1).flat_map(fail).as_result()
    assert isinstance(flat_mapped_result, Right)
    assert isinstance(flat_mapped_result.value, ValueError)

    assert mapped.maybe_success() is None
    assert isinstance(mapped.maybe_exception(), Right)



def test_fallible_flat_map_step_may_capture_other_exceptions() -> None:
    table = {1: "one"}

    def look_up(text: str) -> Fallible[str, ValueError | KeyError]:
        parsed = Fallible(lambda: int(text), ValueError)
        return parsed.flat_map(lambda number: Fallible(lambda: table[number], KeyError))

    assert_type(look_up("1"), Fallible[str, ValueError | KeyError])
    assert look_up("1").as_result() == Left("one")
    parse_failed = look_up("x").maybe_exception()
    assert parse_failed is not None and isinstance(parse_failed.value, ValueError)
    lookup_failed = look_up("2").maybe_exception()
    assert lookup_failed is not None and isinstance(lookup_failed.value, KeyError)

def test_fallible_does_not_swallow_base_exceptions() -> None:
    def interrupt() -> Never:
        raise KeyboardInterrupt

    with pytest.raises(KeyboardInterrupt):
        Fallible(interrupt)


def test_fallible_only_captures_selected_exceptions() -> None:
    captured = Fallible(lambda: int("not a number"), ValueError)
    failed = captured.maybe_exception()
    assert isinstance(failed, Right)
    assert isinstance(failed.value, ValueError)

    with pytest.raises(TypeError):
        Fallible(lambda: len(None), ValueError)  # type: ignore[arg-type]


def test_fallible_accepts_and_preserves_a_tuple_of_exception_types() -> None:
    selected = (ValueError, RuntimeError)
    result = Fallible(lambda: 1, selected).map(
        lambda _: (_ for _ in ()).throw(RuntimeError("mapped failure"))
    )

    failed = result.maybe_exception()
    assert isinstance(failed, Right)
    assert isinstance(failed.value, RuntimeError)


def test_typed_readme_flow() -> None:
    def categorise(number: int) -> Either[Literal["A"], Literal["B"]]:
        if number == 0:
            return Either.new("A")
        return Either.right("B")

    assert [item.is_left() for item in map(categorise, [0, 1, 0])] == [True, False, True]



def test_validation_reports_every_independent_failure_together() -> None:
    def check(name: str, ok: bool) -> Validation[str, str]:
        if ok:
            return Validation.new(name)
        return Validation.invalid(f"{name} failed")

    checks = [check("a", True), check("b", False), check("c", True), check("d", False)]
    combined = Validation.sequence(*checks)

    assert_type(combined, Validation[tuple[str, ...], str])
    assert combined == Invalid(("b failed", "d failed"))
    assert Validation.sequence(*checks[::2]) == Valid(("a", "c"))
    assert Validation.sequence() == Valid(())


def test_validation_sequence_keeps_each_type_of_a_fixed_set() -> None:
    count: Validation[int, ValueError] = Validation.new(1)
    name: Validation[str, KeyError] = Validation.new("a")
    flag: Validation[bool, TypeError] = Validation.invalid(TypeError("flag"))

    assert_type(Validation.sequence(count), Validation[tuple[int], ValueError])
    assert_type(Validation.sequence(count, name), Validation[tuple[int, str], ValueError | KeyError])
    three = Validation.sequence(count, name, flag)
    assert_type(three, Validation[tuple[int, str, bool], ValueError | KeyError | TypeError])
    six = Validation.sequence(count, name, count, name, count, name)
    assert_type(six, Validation[tuple[int, str, int, str, int, str], ValueError | KeyError])

    assert Validation.sequence(count, name) == Valid((1, "a"))
    failed = three.maybe_invalid()
    assert failed is not None and [type(error) for error in failed.errors] == [TypeError]


def test_validation_sequence_lazy_makes_nothing_until_called() -> None:
    made: list[str] = []

    def make(name: str, ok: bool) -> Callable[[], Validation[str, str]]:
        def maker() -> Validation[str, str]:
            made.append(name)
            return Validation[str, str].new(name) if ok else Validation[str, str].invalid(name)

        return maker

    makers = [make("a", True), make("b", False), make("c", False)]
    assert made == []

    assert Validation.sequence_lazy(*makers) == Invalid(("b", "c"))
    assert made == ["a", "b", "c"]

    with ThreadPoolExecutor() as executor:
        together = Validation.sequence_lazy(make("d", True), make("e", True), executor=executor)
    assert_type(together, Validation[tuple[str, str], str])
    assert together == Valid(("d", "e"))


def test_validation_sequence_lazy_lets_a_raising_function_propagate() -> None:
    def broken() -> Validation[int, str]:
        raise RuntimeError("a bug, not an error to collect")

    with pytest.raises(RuntimeError, match="a bug"):
        Validation.sequence_lazy(lambda: Validation[int, str].new(1), broken)


def test_validation_flat_map_runs_a_dependent_step_and_widens_its_errors() -> None:
    registry: Validation[int, ValueError] = Validation.new(2)

    def credentials_for(accounts: int) -> Validation[str, KeyError]:
        if accounts > 1:
            return Validation.new(f"{accounts} accounts")
        return Validation.invalid(KeyError(accounts))

    chained = registry.flat_map(credentials_for)
    assert_type(chained, Validation[str, ValueError | KeyError])
    assert chained == Valid("2 accounts")

    missing: Validation[int, ValueError] = Validation.invalid(ValueError("no registry"))
    assert missing.flat_map(credentials_for).maybe_invalid() is not None
    assert Validation[int, ValueError].new(1).flat_map(credentials_for).is_invalid()


def test_validation_mixes_dependent_and_independent_steps() -> None:
    def load_registry() -> Validation[int, ValueError]:
        return Validation.invalid(ValueError("no registry"))

    def credentials_for(accounts: int) -> Validation[str, KeyError]:  # pragma: no cover - never reached
        return Validation.new(str(accounts))

    def load_rates() -> Validation[float, LookupError]:
        return Validation.invalid(LookupError("no rates"))

    ready = Validation.sequence(
        load_registry().flat_map(lambda accounts: credentials_for(accounts).map(lambda credentials: (accounts, credentials))),
        load_rates(),
    )

    assert_type(ready, Validation[tuple[tuple[int, str], float], ValueError | KeyError | LookupError])
    assert ready.map_invalid(str).or_else(list) == ["no registry", "no rates"]


def test_validation_invalid_holds_at_least_one_error() -> None:
    with pytest.raises(ValueError, match="at least one error"):
        Invalid[str, int](())


def test_validation_operations() -> None:
    valid: Validation[int, str] = Validation.new(1)
    invalid: Validation[int, str] = Invalid(("bad", "worse"))

    assert valid.map(lambda value: value + 1) == Valid(2)
    assert valid.narrow() == Some(1)
    assert valid.or_else(len) == 1
    assert valid.as_either() == Left(1)
    assert invalid.map_invalid(str.upper) == Invalid(("BAD", "WORSE"))
    assert invalid.recover_with(lambda errors: Validation[int, str].new(len(errors))) == Valid(2)
    assert invalid.or_else(len) == 2
    assert invalid.as_either() == Right(("bad", "worse"))


def test_validation_variant_guards_narrow_to_concrete_cases() -> None:
    validation: Validation[int, str] = Validation.invalid("bad")
    assert_type(validation.maybe_valid(), Valid[int, str] | None)
    if invalid := validation.maybe_invalid():
        assert_type(invalid, Invalid[str, int])
        assert invalid.errors == ("bad",)
    else:  # pragma: no cover - protects type narrowing at runtime
        pytest.fail("expected invalid")

    match Validation[int, str].new(0):
        case Valid(value):
            assert value == 0
        case Invalid():  # pragma: no cover - protects exhaustiveness at runtime
            pytest.fail("unexpected invalid")


def test_fallible_refusals_become_validations_and_combine() -> None:
    def refuse(message: str) -> list[int]:
        raise ValueError(message)

    pulls = [
        Fallible(lambda: [1], ValueError).as_validation(),
        Fallible(lambda: refuse("first"), ValueError).as_validation(),
        Fallible(lambda: refuse("second"), ValueError).as_validation(),
    ]
    combined = Validation.sequence(*pulls)

    assert_type(combined, Validation[tuple[list[int], ...], ValueError])
    assert combined.map_invalid(str).or_else(list) == ["first", "second"]
