"""Consumer typing contracts, checked by strict mypy and strict pyright."""

from typing import Never, assert_type

from uogtad import Either, Empty, Invalid, Left, Maybe, Right, Some, Valid, Validation


def bare_factories(value: int, error: str, optional: int | None) -> None:
    assert_type(Either.new(value), Either[int, Never])
    assert_type(Either.right(error), Either[Never, str])
    assert_type(Maybe.new(value), Maybe[int])
    assert_type(Maybe.new(None), Maybe[None])
    assert_type(Maybe.empty(), Maybe[Never])
    assert_type(Maybe.of_optional(optional), Maybe[int])
    assert_type(Maybe.of_optional(None), Maybe[Never])
    assert_type(Validation.new(value), Validation[int, Never])
    assert_type(Validation.invalid(error), Validation[Never, str])


def specialised_factories(value: int, error: str, optional: int | None) -> None:
    assert_type(Either[int, str].new(value), Either[int, str])
    assert_type(Either[int, str].right(error), Either[int, str])
    assert_type(Maybe[int].new(value), Maybe[int])
    assert_type(Maybe[int].empty(), Maybe[int])
    assert_type(Maybe[int].of_optional(optional), Maybe[int])
    assert_type(Validation[int, str].new(value), Validation[int, str])
    assert_type(Validation[int, str].invalid(error), Validation[int, str])


def contextual_factories(value: int, error: str, optional: int | None) -> None:
    either: Either[int, str] = Either.new(value)
    right: Either[int, str] = Either.right(error)
    maybe: Maybe[int] = Maybe.new(value)
    empty: Maybe[int] = Maybe.empty()
    from_optional: Maybe[int] = Maybe.of_optional(optional)
    valid: Validation[int, str] = Validation.new(value)
    invalid: Validation[int, str] = Validation.invalid(error)
    assert_type(either, Either[int, str])
    assert_type(right, Either[int, str])
    assert_type(maybe, Maybe[int])
    assert_type(empty, Maybe[int])
    assert_type(from_optional, Maybe[int])
    assert_type(valid, Validation[int, str])
    assert_type(invalid, Validation[int, str])


def literal_and_none_factories() -> None:
    assert_type(Either.new(1), Either[int, Never])
    assert_type(Either.new(None), Either[None, Never])
    assert_type(Either.right(None), Either[Never, None])
    assert_type(Maybe.new(0), Maybe[int])
    assert_type(Maybe.new(False), Maybe[bool])
    assert_type(Maybe.of_optional(1), Maybe[int])
    assert_type(Validation.new(1), Validation[int, Never])
    assert_type(Validation.new(None), Validation[None, Never])
    assert_type(Validation.invalid(None), Validation[Never, None])


def wider_specialisations(value: int, error: ValueError) -> None:
    assert_type(Either[object, Exception].new(value), Either[object, Exception])
    assert_type(Either[object, Exception].right(error), Either[object, Exception])
    assert_type(Maybe[object].new(value), Maybe[object])
    assert_type(Maybe[int | None].new(None), Maybe[int | None])
    assert_type(Maybe[int | None].of_optional(None), Maybe[int | None])
    assert_type(Validation[object, Exception].new(value), Validation[object, Exception])
    assert_type(Validation[object, Exception].invalid(error), Validation[object, Exception])


def wrap[T](value: T) -> Either[T, str]:
    return Either.new(value)


def downstream_inference() -> None:
    assert_type(Either.new(1).map(str), Either[str, Never])
    assert_type(Either.new(1).flat_map(wrap), Either[int, str])
    assert_type(Maybe.new(1).map(str), Maybe[str])
    assert_type(Validation.new(1).map(str), Validation[str, Never])
    make = Either.new
    assert_type(make(1), Either[int, Never])

    # The README's annotated inputs must keep their error types when sequenced.
    count: Validation[int, ValueError] = Validation.new(1)
    name: Validation[str, KeyError] = Validation.new("a")
    assert_type(Validation.sequence(count, name), Validation[tuple[int, str], ValueError | KeyError])
    assert_type(
        Validation.sequence_lazy(lambda: count, lambda: name),
        Validation[tuple[int, str], ValueError | KeyError],
    )


def concrete_constructors() -> None:
    # Base-class defaults must not change inference on the concrete cases.
    assert_type(Left(1), Left[int, Never])
    assert_type(Right("bad"), Right[str, Never])
    assert_type(Some(None), Some[None])
    assert_type(Empty(), Empty[Never])
    assert_type(Valid(1), Valid[int, Never])
    assert_type(Invalid(("bad",)), Invalid[str, Never])
    assert_type(Maybe(1), Maybe[int])
