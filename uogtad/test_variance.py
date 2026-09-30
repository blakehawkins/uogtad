"""Each container is covariant: a narrower one stands where a wider one is expected."""

from typing import Never

from uogtad import Either, Empty, Fallible, Invalid, Left, Maybe, Right, Some, Valid, Validation


def test_containers_are_covariant() -> None:
    either: Either[bool, ValueError] = Either.new(True)
    wider_either: Either[int, Exception] = either
    maybe: Maybe[bool] = Maybe.new(True)
    wider_maybe: Maybe[int] = maybe
    validation: Validation[bool, ValueError] = Validation.new(True)
    wider_validation: Validation[int, Exception] = validation
    fallible: Fallible[bool, ValueError] = Fallible(lambda: True, ValueError)
    wider_fallible: Fallible[int, Exception] = fallible
    assert (wider_either, wider_maybe, wider_validation, wider_fallible) is not None


def test_cases_are_covariant() -> None:
    left: Left[bool, Never] = Left(True)
    wider_left: Left[int, Exception] = left
    right: Right[ValueError, Never] = Right(ValueError())
    wider_right: Right[Exception, int] = right
    some: Some[bool] = Some(True)
    wider_some: Some[int] = some
    empty: Empty[bool] = Empty()
    wider_empty: Empty[int] = empty
    valid: Valid[bool, Never] = Valid(True)
    wider_valid: Valid[int, Exception] = valid
    invalid: Invalid[ValueError, Never] = Invalid((ValueError(),))
    wider_invalid: Invalid[Exception, int] = invalid
    assert (wider_left, wider_right, wider_some, wider_empty, wider_valid, wider_invalid) is not None
