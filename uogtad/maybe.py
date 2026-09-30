"""The optional-value :class:`Maybe` container."""

from dataclasses import dataclass
from typing import Callable, Generic, Never, TypeVar

from uogtad.either import Either, Left, Right


# Covariant, and declared, for the reasons Either's type variables are.
T = TypeVar("T", covariant=True)


class Maybe(Generic[T]):
    """A value represented by either :class:`Some` or :class:`Empty`.

    ``Maybe(value)`` creates ``Some(value)``. Unlike the previous implementation,
    ``None`` is a valid present value.
    """

    def __new__(cls, value: T) -> Maybe[T]:
        return Some(value)

    @classmethod
    def new[V](cls: type[Maybe[V]], value: V) -> Maybe[V]:
        """Create a present value, including when ``value`` is falsy."""
        return Some(value)

    @classmethod
    def empty[V](cls: type[Maybe[V]]) -> Maybe[V]:
        return Empty[V]()

    @classmethod
    def of_optional[V](cls: type[Maybe[V]], value: V | None) -> Maybe[V]:
        """Create ``Empty`` from ``None`` and ``Some`` from any other value."""
        match value:
            case None:
                return Empty[V]()
            case _:
                return Some(value)

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
                return Either[T, RuntimeError].new(value)
            case Empty():
                return Either[T, RuntimeError].right(RuntimeError(context))
            case _:
                raise TypeError("unknown Maybe variant")

    def or_else[V](self, instead: V) -> T | V:
        if (some := self.maybe_some()) is not None:
            return some.value
        return instead

    def or_else_get[V](self, instead_provider: Callable[[], V]) -> T | V:
        if (some := self.maybe_some()) is not None:
            return some.value
        return instead_provider()

    def filter(self, clause: Callable[[T], bool]) -> Maybe[T]:
        match self:
            case Some(value) if clause(value):
                return Some(value)
            case Some() | Empty():
                return Empty[T]()
            case _:
                raise TypeError("unknown Maybe variant")

    def map[V](self, function: Callable[[T], V]) -> Maybe[V]:
        match self:
            case Some(value):
                return Some(function(value))
            case Empty():
                return Empty[V]()
            case _:
                raise TypeError("unknown Maybe variant")

    def narrow(self) -> T | None:
        if (some := self.maybe_some()) is not None:
            return some.value
        return None

    def flat_map[V](self, function: Callable[[T], Maybe[V]]) -> Maybe[V]:
        match self:
            case Some(value):
                return function(value)
            case Empty():
                return Empty[V]()
            case _:
                raise TypeError("unknown Maybe variant")


# The cases are declared covariant for the same reasons as Maybe, and Empty's
# type defaults to Never. Some's field is ignored by mypy as Left's is.
Absent = TypeVar("Absent", covariant=True, default=Never)


@dataclass(frozen=True)
class Some(Maybe[T]):
    """The present case of :class:`Maybe`."""

    value: T  # type: ignore[misc]

    def __new__(cls, value: T) -> Some[T]:
        return object.__new__(cls)


@dataclass(frozen=True)
class Empty(Maybe[Absent]):
    """The absent case of :class:`Maybe`."""

    def __new__(cls) -> Empty[Absent]:
        return object.__new__(cls)


__all__ = ["Maybe", "Some", "Empty"]
