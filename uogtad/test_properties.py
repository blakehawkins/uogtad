"""Property-based tests for the public container laws and invariants."""

from collections.abc import Callable

from hypothesis import given
from hypothesis import strategies as st

from uogtad import Either, Empty, Fallible, Invalid, Left, Maybe, Right, Some, Valid, Validation


values = st.one_of(
    st.none(),
    st.booleans(),
    st.integers(),
    st.text(),
    st.lists(st.integers()),
)


@given(values)
def test_either_left_has_exactly_one_variant(value: object) -> None:
    result: Either[object, object] = Either.new(value)

    assert result.is_left()
    assert not result.is_right()
    assert result.maybe_left() == Left(value)
    assert result.maybe_right() is None
    assert result.narrow() == Some(value)


@given(values)
def test_either_right_has_exactly_one_variant(value: object) -> None:
    result: Either[object, object] = Either.right(value)

    assert not result.is_left()
    assert result.is_right()
    assert result.maybe_left() is None
    assert result.maybe_right() == Right(value)
    assert result.narrow() == Empty()


@given(values, st.booleans())
def test_either_swap_is_an_involution(value: object, is_left: bool) -> None:
    result: Either[object, object]
    if is_left:
        result = Either.new(value)
    else:
        result = Either.right(value)

    assert result.swap().swap() == result


@given(st.integers(), st.integers(), st.integers())
def test_either_map_obeys_identity_and_composition(value: int, addend: int, factor: int) -> None:
    result: Either[int, str] = Either.new(value)

    def add(item: int) -> int:
        return item + addend

    def multiply(item: int) -> int:
        return item * factor

    assert result.map(lambda item: item) == result
    assert result.map(add).map(multiply) == result.map(lambda item: multiply(add(item)))


@given(st.text(), st.text())
def test_either_right_short_circuits_left_operations(value: str, fallback: str) -> None:
    result: Either[int, str] = Either.right(value)
    called = False

    def left_callback(_: int) -> int:
        nonlocal called
        called = True
        return 0

    assert result.map(left_callback) == Right(value)
    assert result.flat_map(lambda item: Either.new(left_callback(item))) == Right(value)
    assert result.or_else(lambda _: fallback) == fallback
    assert not called


@given(values)
def test_maybe_new_always_creates_some(value: object) -> None:
    result = Maybe.new(value)

    assert result == Some(value)
    assert result.is_present()
    assert result.maybe_some() == Some(value)
    assert result.narrow() == value


@given(values)
def test_maybe_of_optional_matches_none_semantics(value: object) -> None:
    result = Maybe.of_optional(value)

    if value is None:
        assert result == Empty()
    else:
        assert result == Some(value)


@given(st.integers(), st.integers(), st.integers())
def test_maybe_map_obeys_identity_and_composition(value: int, addend: int, factor: int) -> None:
    result = Maybe.new(value)

    def add(item: int) -> int:
        return item + addend

    def multiply(item: int) -> int:
        return item * factor

    assert result.map(lambda item: item) == result
    assert result.map(add).map(multiply) == result.map(lambda item: multiply(add(item)))


@given(st.integers(), st.integers())
def test_maybe_filter_matches_predicate(value: int, divisor: int) -> None:
    predicate: Callable[[int], bool] = lambda item: item >= divisor
    expected: Maybe[int] = Some(value) if predicate(value) else Empty()

    assert Maybe.new(value).filter(predicate) == expected


@given(values, values)
def test_maybe_fallbacks_are_lazy_for_present_values(value: object, fallback: object) -> None:
    called = False

    def fallback_provider() -> object:
        nonlocal called
        called = True
        return fallback

    assert Maybe.new(value).or_else(fallback) == value
    assert Maybe.new(value).or_else_get(fallback_provider) == value
    assert not called


@given(st.integers())
def test_fallible_success_round_trips_and_maps(value: int) -> None:
    result = Fallible(lambda: value)

    assert result.is_success()
    assert not result.is_exception()
    assert result.as_result() == Left(value)
    assert result.narrow() == Some(value)
    assert result.map(lambda item: item + 1).as_result() == Left(value + 1)


@given(st.text(), st.text())
def test_fallible_failure_preserves_exception_and_recovers(message: str, recovery: str) -> None:
    error = ValueError(message)

    def fail() -> int:
        raise error

    result = Fallible(fail)

    assert not result.is_success()
    assert result.is_exception()
    assert result.maybe_success() is None
    assert result.maybe_exception() == Right(error)
    assert result.map(lambda item: item + 1).as_result() == Right(error)
    assert result.or_else(lambda caught: (caught, recovery)) == (error, recovery)



errors = st.lists(st.text(), min_size=1).map(tuple)
validations: st.SearchStrategy[Validation[int, str]] = st.one_of(
    st.integers().map(lambda value: Validation[int, str].new(value)),
    errors.map(lambda found: Invalid[str, int](found)),
)


def _errors(validation: Validation[int, str]) -> tuple[str, ...]:
    return invalid.errors if (invalid := validation.maybe_invalid()) else ()


@given(st.lists(validations))
def test_validation_sequence_keeps_every_value_or_every_error_in_order(items: list[Validation[int, str]]) -> None:
    combined = Validation.sequence(*items)
    found = tuple(error for item in items for error in _errors(item))

    assert combined.is_valid() == all(item.is_valid() for item in items)
    if found:
        assert combined == Invalid(found)
    else:
        assert combined == Valid(tuple(item.or_else(lambda _: 0) for item in items))


@given(st.lists(validations))
def test_validation_sequence_lazy_is_sequence_of_what_it_makes(items: list[Validation[int, str]]) -> None:
    makers = [lambda item=item: item for item in items]

    assert Validation.sequence_lazy(*makers) == Validation.sequence(*items)


@given(validations, st.integers(), st.integers())
def test_validation_map_obeys_identity_and_composition(validation: Validation[int, str], addend: int, factor: int) -> None:
    def add(item: int) -> int:
        return item + addend

    def multiply(item: int) -> int:
        return item * factor

    assert validation.map(lambda item: item) == validation
    assert validation.map(add).map(multiply) == validation.map(lambda item: multiply(add(item)))


@given(st.integers(), validations)
def test_validation_flat_map_on_a_valid_value_is_the_step(value: int, step_result: Validation[int, str]) -> None:
    assert Validation[int, str].new(value).flat_map(lambda _: step_result) == step_result


@given(errors)
def test_validation_invalid_short_circuits_value_operations(found: tuple[str, ...]) -> None:
    validation = Invalid[str, int](found)
    called = False

    def value_callback(_: int) -> int:
        nonlocal called
        called = True
        return 0

    assert validation.map(value_callback) == Invalid(found)
    assert validation.flat_map(lambda item: Validation[int, str].new(value_callback(item))) == Invalid(found)
    assert validation.narrow() == Empty()
    assert not called


@given(validations)
def test_validation_round_trips_through_either(validation: Validation[int, str]) -> None:
    either = validation.as_either()

    assert either.is_left() == validation.is_valid()
    if invalid := validation.maybe_invalid():
        assert either == Right(invalid.errors)
    assert validation.map_invalid(lambda error: error) == validation


@given(values, st.booleans())
def test_either_and_fallible_become_single_error_validations(value: object, is_left: bool) -> None:
    either: Either[object, object] = Either.new(value) if is_left else Either.right(value)

    assert either.as_validation() == (Valid(value) if is_left else Invalid((value,)))

    error = ValueError(value)

    def fail() -> object:
        raise error

    assert Fallible(lambda: value).as_validation() == Valid(value)
    assert Fallible(fail, ValueError).as_validation() == Invalid((error,))
