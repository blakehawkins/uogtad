"""The two-case :class:`Either` container."""

from dataclasses import dataclass
from typing import Callable, Never

class Either[T, U]:
    """A value in exactly one of two cases: :class:`Left` or :class:`Right`."""

    @classmethod
    def new(cls, value: T) -> Either[T, U]:
        """Create a left value (``Either`` is left-biased)."""
        return Left[T, U](value)

    @classmethod
    def right(cls, value: U) -> Either[T, U]:
        """Create a right value."""
        return Right[U, T](value)

    def is_left(self) -> bool:
        match self:
            case Left():
                return True
            case Right():
                return False
            case _:
                raise TypeError("unknown Either variant")

    def is_right(self) -> bool:
        return not self.is_left()

    def maybe_left(self) -> Left[T, U] | None:
        """Return the concrete left variant, or ``None`` when this is right."""
        match self:
            case Left() as left:
                return left
            case Right():
                return None
            case _:
                raise TypeError("unknown Either variant")

    def maybe_right(self) -> Right[U, T] | None:
        """Return the concrete right variant, or ``None`` when this is left."""
        match self:
            case Left():
                return None
            case Right() as right:
                return right
            case _:
                raise TypeError("unknown Either variant")

    def context(self, context: str) -> Either[T, RuntimeError]:
        match self:
            case Left(value):
                return Left(value)
            case Right(value):
                return Right(RuntimeError(context, value))
            case _:
                raise TypeError("unknown Either variant")

    def swap(self) -> Either[U, T]:
        match self:
            case Left(value):
                return Right(value)
            case Right(value):
                return Left(value)
            case _:
                raise TypeError("unknown Either variant")

    def or_else[V](self, otherwise: Callable[[U], V]) -> T | V:
        if (left := self.maybe_left()) is not None:
            return left.value
        if (right := self.maybe_right()) is not None:
            return otherwise(right.value)
        raise TypeError("unknown Either variant")

    def map[V](self, function: Callable[[T], V]) -> Either[V, U]:
        match self:
            case Left(value):
                return Left(function(value))
            case Right(value):
                return Right(value)
            case _:
                raise TypeError("unknown Either variant")

    def flat_map[V](self, function: Callable[[T], Either[V, U]]) -> Either[V, U]:
        match self:
            case Left(value):
                return function(value)
            case Right(value):
                return Right(value)
            case _:
                raise TypeError("unknown Either variant")

    def map_right[V](self, function: Callable[[U], V]) -> Either[T, V]:
        match self:
            case Left(value):
                return Left(value)
            case Right(value):
                return Right(function(value))
            case _:
                raise TypeError("unknown Either variant")

    def flat_map_right[V](self, function: Callable[[U], Either[T, V]]) -> Either[T, V]:
        match self:
            case Left(value):
                return Left(value)
            case Right(value):
                return function(value)
            case _:
                raise TypeError("unknown Either variant")

    def narrow(self) -> Maybe[T]:
        match self:
            case Left(value):
                return Some(value)
            case Right():
                return Empty[T]()
            case _:
                raise TypeError("unknown Either variant")


@dataclass(frozen=True)
class Left[L, R = Never](Either[L, R]):
    """The left case of :class:`Either`."""

    value: L


@dataclass(frozen=True)
class Right[R, L = Never](Either[L, R]):
    """The right case of :class:`Either`."""

    value: R


from uogtad.maybe import Empty, Maybe, Some  # noqa: E402

__all__ = ["Either", "Left", "Right"]
