from typing import Literal, Never

import pytest

from uogtad import Either, Empty, Fallible, Left, Maybe, Right, Some


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


def test_fallible_does_not_swallow_base_exceptions() -> None:
    def interrupt() -> Never:
        raise KeyboardInterrupt

    with pytest.raises(KeyboardInterrupt):
        Fallible(interrupt)


def test_typed_readme_flow() -> None:
    def categorise(number: int) -> Either[Literal["A"], Literal["B"]]:
        if number == 0:
            return Either.new("A")
        return Either.right("B")

    assert [item.value for item in map(categorise, [0, 1, 0]) if isinstance(item, Left)] == ["A", "A"]
