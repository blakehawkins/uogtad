"""The optional-value :class:`Maybe` container."""

from dataclasses import dataclass
from typing import Callable, Never

from uogtad._typing import narrowed
from uogtad.either import Either, Left, Right


class Maybe[T]:
    """A value represented by either :class:`Some` or :class:`Empty`.

    ``Maybe(value)`` creates ``Some(value)``. Unlike the previous implementation,
    ``None`` is a valid present value.
    """

    def __new__[V](cls, value: V) -> Maybe[V]:
        return Some(value)

    @classmethod
    def new[V](cls, value: V) -> Maybe[V]:
        """Create a present value, including when ``value`` is falsy."""
        return Some(value)

    @classmethod
    def empty[V](cls, _type: type[V] | None = None) -> Maybe[V]:
        return narrowed(Empty())

    def is_present(self) -> bool:
        match self:
            case Some():
                return True
            case Empty():
                return False
            case _:
                raise TypeError("unknown Maybe variant")

    def maybe_some(self) -> Some[T] | None:
        """Return the concrete present variant, or ``None`` when empty."""
        match self:
            case Some() as some:
                return some
            case Empty():
                return None
            case _:
                raise TypeError("unknown Maybe variant")

    def context(self, context: str) -> Either[T, RuntimeError]:
        match self:
            case Some(value):
                return narrowed(Left(value))
            case Empty():
                return narrowed(Right(RuntimeError(context)))
            case _:
                raise TypeError("unknown Maybe variant")

    def or_else[V](self, instead: V) -> T | V:
        match self:
            case Some(value):
                return narrowed(value)
            case Empty():
                return instead
            case _:
                raise TypeError("unknown Maybe variant")

    def or_else_get[V](self, instead_provider: Callable[[], V]) -> T | V:
        match self:
            case Some(value):
                return narrowed(value)
            case Empty():
                return instead_provider()
            case _:
                raise TypeError("unknown Maybe variant")

    def filter(self, clause: Callable[[T], bool]) -> Maybe[T]:
        match self:
            case Some(value) if clause(value):
                return Some(value)
            case Some() | Empty():
                return narrowed(Empty())
            case _:
                raise TypeError("unknown Maybe variant")

    def map[V](self, function: Callable[[T], V]) -> Maybe[V]:
        match self:
            case Some(value):
                return Some(function(value))
            case Empty():
                return narrowed(Empty())
            case _:
                raise TypeError("unknown Maybe variant")

    def narrow(self) -> T | None:
        match self:
            case Some(value):
                return narrowed(value)
            case Empty():
                return None
            case _:
                raise TypeError("unknown Maybe variant")

    def flat_map[V](self, function: Callable[[T], Maybe[V]]) -> Maybe[V]:
        match self:
            case Some(value):
                return function(value)
            case Empty():
                return narrowed(Empty())
            case _:
                raise TypeError("unknown Maybe variant")


@dataclass(frozen=True)
class Some[L](Maybe[L]):
    """The present case of :class:`Maybe`."""

    value: L

    def __new__(cls, value: L) -> Some[L]:
        return object.__new__(cls)


@dataclass(frozen=True)
class Empty(Maybe[Never]):
    """The absent case of :class:`Maybe`."""

    def __new__(cls) -> Empty:
        return object.__new__(cls)


__all__ = ["Maybe", "Some", "Empty"]
