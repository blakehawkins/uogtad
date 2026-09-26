"""The two-case :class:`Either` container."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable, Never, cast

if TYPE_CHECKING:
    from uogtad.maybe import Maybe


class Either[T, U]:
    """A value in exactly one of two cases: :class:`Left` or :class:`Right`."""

    @classmethod
    def new[V, E](cls, value: V) -> "Either[V, E]":  # pyright: ignore[reportInvalidTypeVarUse]
        """Create a left value (``Either`` is left-biased)."""
        return cast(Either[V, E], Left(value))

    @classmethod
    def right[S, V](cls, value: V) -> "Either[S, V]":  # pyright: ignore[reportInvalidTypeVarUse]
        """Create a right value."""
        return cast(Either[S, V], Right(value))

    def is_left(self) -> bool:
        return isinstance(self, Left)

    def is_right(self) -> bool:
        return isinstance(self, Right)

    def context(self, context: str) -> "Either[T, RuntimeError]":
        if isinstance(self, Left):
            return cast(Either[T, RuntimeError], self)
        return cast(Either[T, RuntimeError], Right(RuntimeError(context, cast(Right[U], self).value)))

    def swap(self) -> "Either[U, T]":
        if isinstance(self, Left):
            return cast(Either[U, T], Right(self.value))
        return cast(Either[U, T], Left(cast(Right[U], self).value))

    def or_else[V](self, otherwise: Callable[[U], V]) -> T | V:
        if isinstance(self, Left):
            return cast(Left[T], self).value
        return otherwise(cast(Right[U], self).value)

    def map[V](self, function: Callable[[T], V]) -> "Either[V, U]":
        if isinstance(self, Left):
            return cast(Either[V, U], Left(function(self.value)))
        return cast(Either[V, U], self)

    def flat_map[V](self, function: Callable[[T], "Either[V, U]"]) -> "Either[V, U]":
        if isinstance(self, Left):
            return function(self.value)
        return cast(Either[V, U], self)

    def map_right[V](self, function: Callable[[U], V]) -> "Either[T, V]":
        if isinstance(self, Right):
            return cast(Either[T, V], Right(function(self.value)))
        return cast(Either[T, V], self)

    def flat_map_right[V](self, function: Callable[[U], "Either[T, V]"]) -> "Either[T, V]":
        if isinstance(self, Right):
            return function(self.value)
        return cast(Either[T, V], self)

    def narrow(self) -> "Maybe[T]":
        from uogtad.maybe import Empty, Some

        if isinstance(self, Left):
            return Some(self.value)
        return cast(Maybe[T], Empty())

    def if_left(self, then_: Callable[[T], object]) -> None:
        if isinstance(self, Left):
            then_(self.value)

    def if_right(self, then_: Callable[[U], object]) -> None:
        if isinstance(self, Right):
            then_(self.value)


@dataclass(frozen=True)
class Left[L](Either[L, Never]):
    """The left case of :class:`Either`."""

    value: L


@dataclass(frozen=True)
class Right[R](Either[Never, R]):
    """The right case of :class:`Either`."""

    value: R


__all__ = ["Either", "Left", "Right"]
