"""The error-accumulating :class:`Validation` container."""

from collections.abc import Callable
from concurrent.futures import Executor
from dataclasses import dataclass
from typing import Any, Generic, Never, TypeVar, overload

from uogtad.either import Either, Left, Right
from uogtad.maybe import Empty, Maybe, Some


# Covariant, and declared, for the reasons Either's type variables are.
T = TypeVar("T", covariant=True)
E = TypeVar("E", covariant=True)


class Validation(Generic[T, E]):
    """A value, or every error that prevented one: :class:`Valid` or :class:`Invalid`.

    Validations that do not depend on each other are combined with
    :meth:`sequence`, which keeps the errors of all of them: every check
    runs, and every failure is reported together. A step that needs a
    validation's value is chained with :meth:`flat_map`, which cannot run
    without that value, and so stops at the first invalid validation.
    """

    @classmethod
    def new[V, F](cls: type[Validation[V, F]], value: V) -> Validation[V, F]:
        """Create a valid value."""
        return Valid[V, F](value)

    @classmethod
    def invalid[V, F](cls: type[Validation[V, F]], error: F) -> Validation[V, F]:
        """Create an invalid validation holding one error."""
        return Invalid[F, V]((error,))

    @overload
    @staticmethod
    def sequence[A1, E1](first: Validation[A1, E1], /) -> Validation[tuple[A1], E1]: ...

    @overload
    @staticmethod
    def sequence[A1, A2, E1, E2](
        first: Validation[A1, E1], second: Validation[A2, E2], /
    ) -> Validation[tuple[A1, A2], E1 | E2]: ...

    @overload
    @staticmethod
    def sequence[A1, A2, A3, E1, E2, E3](
        first: Validation[A1, E1], second: Validation[A2, E2], third: Validation[A3, E3], /
    ) -> Validation[tuple[A1, A2, A3], E1 | E2 | E3]: ...

    @overload
    @staticmethod
    def sequence[A1, A2, A3, A4, E1, E2, E3, E4](
        first: Validation[A1, E1],
        second: Validation[A2, E2],
        third: Validation[A3, E3],
        fourth: Validation[A4, E4],
        /,
    ) -> Validation[tuple[A1, A2, A3, A4], E1 | E2 | E3 | E4]: ...

    @overload
    @staticmethod
    def sequence[A1, A2, A3, A4, A5, E1, E2, E3, E4, E5](
        first: Validation[A1, E1],
        second: Validation[A2, E2],
        third: Validation[A3, E3],
        fourth: Validation[A4, E4],
        fifth: Validation[A5, E5],
        /,
    ) -> Validation[tuple[A1, A2, A3, A4, A5], E1 | E2 | E3 | E4 | E5]: ...

    @overload
    @staticmethod
    def sequence[A1, A2, A3, A4, A5, A6, E1, E2, E3, E4, E5, E6](
        first: Validation[A1, E1],
        second: Validation[A2, E2],
        third: Validation[A3, E3],
        fourth: Validation[A4, E4],
        fifth: Validation[A5, E5],
        sixth: Validation[A6, E6],
        /,
    ) -> Validation[tuple[A1, A2, A3, A4, A5, A6], E1 | E2 | E3 | E4 | E5 | E6]: ...

    @overload
    @staticmethod
    def sequence[V, F](*validations: Validation[V, F]) -> Validation[tuple[V, ...], F]: ...

    @staticmethod
    def sequence(*validations: Validation[Any, Any]) -> Validation[tuple[Any, ...], Any]:
        """Every value, in order, or, if any is invalid, every error, in order.

        Given up to six validations, a type checker knows each one's type in
        the tuple. Given more, they are all still combined, but it sees only a
        type they have in common, since Python's type system cannot name one
        type per argument for any number of arguments. Any number of one type
        gives a tuple of that type.
        """
        values: list[Any] = []
        errors: list[Any] = []
        for validation in validations:
            match validation:
                case Valid(value):
                    values.append(value)
                case Invalid(found):
                    errors.extend(found)
                case _:
                    raise TypeError("unknown Validation variant")
        if errors:
            return Invalid(tuple(errors))
        return Valid(tuple(values))

    @overload
    @staticmethod
    def sequence_lazy[A1, E1](
        first: Callable[[], Validation[A1, E1]], /, *, executor: Executor | None = None
    ) -> Validation[tuple[A1], E1]: ...

    @overload
    @staticmethod
    def sequence_lazy[A1, A2, E1, E2](
        first: Callable[[], Validation[A1, E1]],
        second: Callable[[], Validation[A2, E2]],
        /,
        *,
        executor: Executor | None = None,
    ) -> Validation[tuple[A1, A2], E1 | E2]: ...

    @overload
    @staticmethod
    def sequence_lazy[A1, A2, A3, E1, E2, E3](
        first: Callable[[], Validation[A1, E1]],
        second: Callable[[], Validation[A2, E2]],
        third: Callable[[], Validation[A3, E3]],
        /,
        *,
        executor: Executor | None = None,
    ) -> Validation[tuple[A1, A2, A3], E1 | E2 | E3]: ...

    @overload
    @staticmethod
    def sequence_lazy[A1, A2, A3, A4, E1, E2, E3, E4](
        first: Callable[[], Validation[A1, E1]],
        second: Callable[[], Validation[A2, E2]],
        third: Callable[[], Validation[A3, E3]],
        fourth: Callable[[], Validation[A4, E4]],
        /,
        *,
        executor: Executor | None = None,
    ) -> Validation[tuple[A1, A2, A3, A4], E1 | E2 | E3 | E4]: ...

    @overload
    @staticmethod
    def sequence_lazy[A1, A2, A3, A4, A5, E1, E2, E3, E4, E5](
        first: Callable[[], Validation[A1, E1]],
        second: Callable[[], Validation[A2, E2]],
        third: Callable[[], Validation[A3, E3]],
        fourth: Callable[[], Validation[A4, E4]],
        fifth: Callable[[], Validation[A5, E5]],
        /,
        *,
        executor: Executor | None = None,
    ) -> Validation[tuple[A1, A2, A3, A4, A5], E1 | E2 | E3 | E4 | E5]: ...

    @overload
    @staticmethod
    def sequence_lazy[A1, A2, A3, A4, A5, A6, E1, E2, E3, E4, E5, E6](
        first: Callable[[], Validation[A1, E1]],
        second: Callable[[], Validation[A2, E2]],
        third: Callable[[], Validation[A3, E3]],
        fourth: Callable[[], Validation[A4, E4]],
        fifth: Callable[[], Validation[A5, E5]],
        sixth: Callable[[], Validation[A6, E6]],
        /,
        *,
        executor: Executor | None = None,
    ) -> Validation[tuple[A1, A2, A3, A4, A5, A6], E1 | E2 | E3 | E4 | E5 | E6]: ...

    @overload
    @staticmethod
    def sequence_lazy[V, F](
        *makers: Callable[[], Validation[V, F]], executor: Executor | None = None
    ) -> Validation[tuple[V, ...], F]: ...

    @staticmethod
    def sequence_lazy(
        *makers: Callable[[], Validation[Any, Any]], executor: Executor | None = None
    ) -> Validation[tuple[Any, ...], Any]:
        """:meth:`sequence` of what each function makes.

        Nothing is made until this is called. Given an ``executor``, the
        functions run on it, together; otherwise they run in order. A function
        that raises is a bug rather than an error to collect, so its exception
        propagates: a refusal should be made into an error inside it, for
        example with :meth:`~uogtad.Fallible.as_validation`.
        """
        if executor is None:
            made = [make() for make in makers]
        else:
            made = list(executor.map(lambda make: make(), makers))
        return Validation.sequence(*made)

    def is_valid(self) -> bool:
        match self:
            case Valid():
                return True
            case Invalid():
                return False
            case _:
                raise TypeError("unknown Validation variant")

    def is_invalid(self) -> bool:
        return not self.is_valid()

    def maybe_valid(self) -> Valid[T, E] | None:
        """Return the concrete valid variant, or ``None`` when this is invalid."""
        match self:
            case Valid() as valid:
                return valid
            case Invalid():
                return None
            case _:
                raise TypeError("unknown Validation variant")

    def maybe_invalid(self) -> Invalid[E, T] | None:
        """Return the concrete invalid variant, or ``None`` when this is valid."""
        match self:
            case Valid():
                return None
            case Invalid() as invalid:
                return invalid
            case _:
                raise TypeError("unknown Validation variant")

    def map[V](self, function: Callable[[T], V]) -> Validation[V, E]:
        """Transform the value; an invalid validation is returned as it is."""
        match self:
            case Valid(value):
                return Valid(function(value))
            case Invalid(errors):
                return Invalid(errors)
            case _:
                raise TypeError("unknown Validation variant")

    def flat_map[U, F](self, step: Callable[[T], Validation[U, F]]) -> Validation[U, E | F]:
        """Run a step that needs the value.

        .. warning::
            Unlike :meth:`sequence`, this does not accumulate errors. An
            invalid validation has no value to give the step, so it is
            returned as it is, without running it, and a chain of steps stops
            at the first invalid one. Combine validations that do not depend
            on each other with :meth:`sequence`, which keeps every error.
        """
        match self:
            case Valid(value):
                return step(value)
            case Invalid(errors):
                return Invalid[E | F, U](errors)
            case _:
                raise TypeError("unknown Validation variant")

    def map_invalid[F](self, function: Callable[[E], F]) -> Validation[T, F]:
        """Transform each error; a valid validation is returned as it is."""
        match self:
            case Valid(value):
                return Valid(value)
            case Invalid(errors):
                return Invalid(tuple(function(error) for error in errors))
            case _:
                raise TypeError("unknown Validation variant")

    def recover_with[U, F](self, function: Callable[[tuple[E, ...]], Validation[U, F]]) -> Validation[T | U, F]:
        """Recover from every error at once, or replace them."""
        match self:
            case Valid(value):
                return Valid(value)
            case Invalid(errors):
                return function(errors)
            case _:
                raise TypeError("unknown Validation variant")

    def or_else[V](self, recovery: Callable[[tuple[E, ...]], V]) -> T | V:
        if (valid := self.maybe_valid()) is not None:
            return valid.value
        if (invalid := self.maybe_invalid()) is not None:
            return recovery(invalid.errors)
        raise TypeError("unknown Validation variant")

    def narrow(self) -> Maybe[T]:
        match self:
            case Valid(value):
                return Some(value)
            case Invalid():
                return Empty[T]()
            case _:
                raise TypeError("unknown Validation variant")

    def as_either(self) -> Either[T, tuple[E, ...]]:
        match self:
            case Valid(value):
                return Left[T, tuple[E, ...]](value)
            case Invalid(errors):
                return Right[tuple[E, ...], T](errors)
            case _:
                raise TypeError("unknown Validation variant")


# The cases are declared covariant for the same reasons as Validation. Each
# lists its own type first, and the other defaults to Never. Valid's field is
# ignored by mypy as Left's is.
NoErrors = TypeVar("NoErrors", covariant=True, default=Never)
NoValue = TypeVar("NoValue", covariant=True, default=Never)


@dataclass(frozen=True)
class Valid(Validation[T, NoErrors]):
    """The valid case of :class:`Validation`."""

    value: T  # type: ignore[misc]


@dataclass(frozen=True)
class Invalid(Validation[NoValue, E], Generic[E, NoValue]):
    """The invalid case of :class:`Validation`: every error, in the order found."""

    errors: tuple[E, ...]

    def __post_init__(self) -> None:
        if not self.errors:
            raise ValueError("an Invalid validation holds at least one error")


__all__ = ["Validation", "Valid", "Invalid"]
