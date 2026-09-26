"""The exception-capturing :class:`Fallible` container."""

from typing import Callable, cast

from uogtad.either import Either, Left, Right
from uogtad.maybe import Maybe


class Fallible[F]:
    """The successful return value or ordinary exception from a computation."""

    def __init__(self, computation: Callable[[], F]) -> None:
        try:
            self._result: Either[F, Exception] = cast(Either[F, Exception], Left(computation()))
        except Exception as error:
            self._result = cast(Either[F, Exception], Right(error))

    @classmethod
    def _from_result[V](cls, result: Either[V, Exception]) -> "Fallible[V]":
        instance = cast(Fallible[V], cls.__new__(cls))
        instance._result = result
        return instance

    def as_result(self) -> Either[F, Exception]:
        return self._result

    def is_success(self) -> bool:
        return self._result.is_left()

    def is_exception(self) -> bool:
        return self._result.is_right()

    def if_success(self, then_: Callable[[F], object]) -> None:
        self._result.if_left(then_)

    def if_exception(self, then_: Callable[[Exception], object]) -> None:
        self._result.if_right(then_)

    def map[V](self, function: Callable[[F], V]) -> "Fallible[V]":
        if isinstance(self._result, Right):
            return Fallible._from_result(cast(Either[V, Exception], self._result))
        return Fallible(lambda: function(cast(Left[F], self._result).value))

    def flat_map[V](self, function: Callable[[F], "Fallible[V]"]) -> "Fallible[V]":
        if isinstance(self._result, Right):
            return Fallible._from_result(cast(Either[V, Exception], self._result))
        try:
            return function(cast(Left[F], self._result).value)
        except Exception as error:
            return Fallible._from_result(cast(Either[V, Exception], Right(error)))

    def narrow(self) -> Maybe[F]:
        return self._result.narrow()

    def or_else[V](self, recovery: Callable[[Exception], V]) -> F | V:
        return self._result.or_else(recovery)


__all__ = ["Fallible"]
