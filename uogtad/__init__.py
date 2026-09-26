"""Small, typed containers for functional-style control flow."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Generic, Never, TypeVar, cast

T_co = TypeVar("T_co", covariant=True)
U_co = TypeVar("U_co", covariant=True)
V = TypeVar("V")
L = TypeVar("L")
R = TypeVar("R")


class Either(Generic[T_co, U_co]):
    """A value in exactly one of two cases: :class:`Left` or :class:`Right`."""

    @classmethod
    def new(cls, value: V) -> Either[V, Never]:
        """Create a left value (``Either`` is left-biased)."""
        return Left(value)

    @classmethod
    def right(cls, value: V) -> Either[Never, V]:
        """Create a right value."""
        return Right(value)

    def is_left(self) -> bool:
        return isinstance(self, Left)

    def is_right(self) -> bool:
        return isinstance(self, Right)

    def context(self, context: str) -> Either[T_co, RuntimeError]:
        if isinstance(self, Left):
            return self
        return Right(RuntimeError(context, cast(Right[U_co], self).value))

    def swap(self) -> Either[U_co, T_co]:
        if isinstance(self, Left):
            return Right(self.value)
        return Left(cast(Right[U_co], self).value)

    def or_else(self, otherwise: Callable[[U_co], V]) -> T_co | V:
        if isinstance(self, Left):
            return cast(Left[T_co], self).value
        return otherwise(cast(Right[U_co], self).value)

    def map(self, function: Callable[[T_co], V]) -> Either[V, U_co]:
        if isinstance(self, Left):
            return Left(function(self.value))
        return cast(Either[V, U_co], self)

    def flat_map(self, function: Callable[[T_co], Either[V, U_co]]) -> Either[V, U_co]:
        if isinstance(self, Left):
            return function(self.value)
        return cast(Either[V, U_co], self)

    def map_right(self, function: Callable[[U_co], V]) -> Either[T_co, V]:
        if isinstance(self, Right):
            return Right(function(self.value))
        return cast(Either[T_co, V], self)

    def flat_map_right(self, function: Callable[[U_co], Either[T_co, V]]) -> Either[T_co, V]:
        if isinstance(self, Right):
            return function(self.value)
        return cast(Either[T_co, V], self)

    def narrow(self) -> Maybe[T_co]:
        if isinstance(self, Left):
            return Some(self.value)
        return Empty()

    def if_left(self, then_: Callable[[T_co], object]) -> None:
        if isinstance(self, Left):
            then_(self.value)

    def if_right(self, then_: Callable[[U_co], object]) -> None:
        if isinstance(self, Right):
            then_(self.value)


@dataclass(frozen=True)
class Left(Either[L, Never], Generic[L]):
    """The left case of :class:`Either`."""

    value: L


@dataclass(frozen=True)
class Right(Either[Never, R], Generic[R]):
    """The right case of :class:`Either`."""

    value: R


class Maybe(Generic[T_co]):
    """A value represented by either :class:`Some` or :class:`Empty`.

    ``Maybe(value)`` is retained as a convenient spelling for ``Some(value)``;
    unlike the previous implementation, ``None`` is a valid present value.
    """

    def __new__(cls, value: V) -> Maybe[V]:
        if cls is Maybe:
            return cast(Maybe[V], Some(value))
        return cast(Maybe[V], super().__new__(cls))

    @classmethod
    def empty(cls) -> Maybe[Never]:
        return Empty()

    def is_present(self) -> bool:
        return isinstance(self, Some)

    def context(self, context: str) -> Either[T_co, RuntimeError]:
        if isinstance(self, Some):
            return Left(self.value)
        return Right(RuntimeError(context))

    def or_else(self, instead: V) -> T_co | V:
        if isinstance(self, Some):
            return cast(Some[T_co], self).value
        return instead

    def or_else_get(self, instead_provider: Callable[[], V]) -> T_co | V:
        if isinstance(self, Some):
            return cast(Some[T_co], self).value
        return instead_provider()

    def if_present(self, with_: Callable[[T_co], object]) -> None:
        if isinstance(self, Some):
            with_(self.value)

    def filter(self, clause: Callable[[T_co], bool]) -> Maybe[T_co]:
        if isinstance(self, Some) and clause(self.value):
            return self
        return Empty()

    def map(self, function: Callable[[T_co], V]) -> Maybe[V]:
        if isinstance(self, Some):
            return Some(function(self.value))
        return Empty()

    def narrow(self) -> T_co | None:
        if isinstance(self, Some):
            return cast(Some[T_co], self).value
        return None

    def flat_map(self, function: Callable[[T_co], Maybe[V]]) -> Maybe[V]:
        if isinstance(self, Some):
            return function(self.value)
        return Empty()


@dataclass(frozen=True, init=False)
class Some(Maybe[L], Generic[L]):
    """The present case of :class:`Maybe`."""

    value: L

    def __init__(self, value: L) -> None:
        object.__setattr__(self, "value", value)


@dataclass(frozen=True, init=False)
class Empty(Maybe[Never]):
    """The absent case of :class:`Maybe`."""

    def __new__(cls) -> Empty:
        return object.__new__(cls)

    def __init__(self) -> None:
        pass


F_co = TypeVar("F_co", covariant=True)


class Fallible(Generic[F_co]):
    """The successful return value or ordinary exception from a computation."""

    def __init__(self, computation: Callable[[], F_co]) -> None:
        try:
            self._result: Either[F_co, Exception] = Left(computation())
        except Exception as error:
            self._result = Right(error)

    @classmethod
    def _from_result(cls, result: Either[V, Exception]) -> Fallible[V]:
        instance = cast(Fallible[V], cls.__new__(cls))
        instance._result = result
        return instance

    def as_result(self) -> Either[F_co, Exception]:
        return self._result

    def is_success(self) -> bool:
        return self._result.is_left()

    def is_exception(self) -> bool:
        return self._result.is_right()

    def if_success(self, then_: Callable[[F_co], object]) -> None:
        self._result.if_left(then_)

    def if_exception(self, then_: Callable[[Exception], object]) -> None:
        self._result.if_right(then_)

    def map(self, function: Callable[[F_co], V]) -> Fallible[V]:
        if isinstance(self._result, Right):
            return Fallible._from_result(cast(Either[V, Exception], self._result))
        return Fallible(lambda: function(cast(Left[F_co], self._result).value))

    def flat_map(self, function: Callable[[F_co], Fallible[V]]) -> Fallible[V]:
        if isinstance(self._result, Right):
            return Fallible._from_result(cast(Either[V, Exception], self._result))
        try:
            return function(cast(Left[F_co], self._result).value)
        except Exception as error:
            return Fallible._from_result(Right(error))

    def narrow(self) -> Maybe[F_co]:
        return self._result.narrow()

    def or_else(self, recovery: Callable[[Exception], V]) -> F_co | V:
        return self._result.or_else(recovery)


__all__ = ["Either", "Left", "Right", "Maybe", "Some", "Empty", "Fallible"]
