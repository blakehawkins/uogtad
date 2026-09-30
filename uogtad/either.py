"""The two-case :class:`Either` container."""

from dataclasses import dataclass
from typing import Callable, Generic, Never, TypeVar

lazy import uogtad.maybe as maybe_module
lazy import uogtad.validation as validation_module


# Every container is covariant: it is immutable, so an Either[bool, ValueError]
# can stand where an Either[int, Exception] is expected. The class syntax,
# class Either[T, U], can only infer variance, and both checkers infer these
# containers as invariant: pyright because maybe_left and maybe_right return a
# subclass of the class being inferred, and mypy because the constructors take
# their types through cls. So the variance is declared.
T = TypeVar("T", covariant=True)
U = TypeVar("U", covariant=True)


class Either(Generic[T, U]):
    """A value in exactly one of two cases: :class:`Left` or :class:`Right`."""

    # A covariant T or U cannot be a parameter, so the constructors take their
    # types from the class they are called on, as in Either[int, str].new(1).
    @classmethod
    def new[V, W](cls: type[Either[V, W]], value: V) -> Either[V, W]:
        """Create a left value (``Either`` is left-biased)."""
        return Left[V, W](value)

    @classmethod
    def right[V, W](cls: type[Either[V, W]], value: W) -> Either[V, W]:
        """Create a right value."""
        return Right[W, V](value)

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

    def flat_map[V, F](self, function: Callable[[T], Either[V, F]]) -> Either[V, U | F]:
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

    def flat_map_right[S, V](self, function: Callable[[U], Either[S, V]]) -> Either[T | S, V]:
        match self:
            case Left(value):
                return Left(value)
            case Right(value):
                return function(value)
            case _:
                raise TypeError("unknown Either variant")

    def as_validation(self) -> validation_module.Validation[T, U]:
        """A validation of the left value, or of the right value as its one error."""
        match self:
            case Left(value):
                return validation_module.Valid[T, U](value)
            case Right(value):
                return validation_module.Invalid[U, T]((value,))
            case _:
                raise TypeError("unknown Either variant")

    def narrow(self) -> maybe_module.Maybe[T]:
        match self:
            case Left(value):
                return maybe_module.Some(value)
            case Right():
                return maybe_module.Empty[T]()
            case _:
                raise TypeError("unknown Either variant")


# The cases are declared covariant for the same reasons: they inherit
# maybe_left, maybe_right and the constructors. Each lists its own value's type
# first, and the other side's defaults to Never.
#
# mypy objects to each case's field, through the __replace__ that dataclasses
# generate from Python 3.13, which takes the fields as parameters. A frozen
# dataclass's __replace__ makes a new object rather than changing this one, so
# covariance stays sound, and the objection is ignored, in every module's cases.
NoLeft = TypeVar("NoLeft", covariant=True, default=Never)
NoRight = TypeVar("NoRight", covariant=True, default=Never)


@dataclass(frozen=True)
class Left(Either[T, NoRight]):
    """The left case of :class:`Either`."""

    value: T  # type: ignore[misc]


@dataclass(frozen=True)
class Right(Either[NoLeft, U], Generic[U, NoLeft]):
    """The right case of :class:`Either`."""

    value: U  # type: ignore[misc]


__all__ = ["Either", "Left", "Right"]
