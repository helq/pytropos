import typing as ty

from .value import Value, Any
from .rules import binop_rules, BINARY_OP_METHODS

__all__ = ['Int', 'Iterable', 'Float', 'ValueAsWithStmt', 'for_loop']

Pos = ty.Tuple[int, int]


class Iterable(Value):
    val = None  # type: ty.Any

    def __init__(self, val: ty.Any) -> None:
        self.val = val


class Str(Value):
    s = None  # type: str

    def __init__(self, s: str) -> None:
        self.s = s


# TODO(helq): make `n` and all other variables private
# TODO(helq): trying to set an attribute should throw an error (ie, the
# simulation of the basic building blocks (int, float, ...) should be as close
# as possible to the official libraries)
class Int(Value):
    def __init__(self, n: ty.Optional[int] = None) -> None:
        self.n = n

    def __repr__(self) -> str:
        return "Int("+repr(self.n)+")"


def __create_binop_int(  # noqa: C901
        op: ty.Callable[[int, ty.Any], ty.Any],
        output_is_only_int: bool = True
) -> ty.Callable:
    def binop(self: Int,
              other: Value,
              src_pos: ty.Optional[Pos] = None
              ) -> ty.Union[Int, Value, 'NotImplemented']:
        if isinstance(other, Int):
            if self.n is None or other.n is None:
                return Int()

            try:
                # TODO(helq): make sure the operation doesn't take too long or takes too
                # much space. For example, `pow`, `rshift` and `lshift` can take easily
                # many resources with only a simple operation
                new_n = op(self.n, other.n)  # type: ty.Optional[int]
            except ZeroDivisionError:
                # TODO(helq): add warning to list of warnings!
                new_n = None
            except ValueError:
                new_n = None
            except OverflowError:
                new_n = None

            if output_is_only_int:
                if isinstance(new_n, int) or new_n is None:
                    return Int(new_n)

                # TODO(helq): add possible warning, this is a warning not an error, perse
                return Any()  # This will, probably, never happen
            else:
                if isinstance(new_n, float):
                    return Float(new_n)
                elif isinstance(new_n, int):
                    return Int(new_n)
                # This happens if the result is not an int or a float, for example a complex
                return Any()

        return NotImplemented
    return binop


# functions that not always return int as a result
not_always_int = set({
    '__pow__', '__rpow__',
    '__truediv__', '__rtruediv__',
})
for op in BINARY_OP_METHODS:
    alwaysint = op not in not_always_int
    if hasattr(int, op):
        setattr(Int, op, __create_binop_int(getattr(int, op), alwaysint))

binop_rules.extractRulesFromClass(Int)


# TODO(helq): add warning when operating with nan values
class Float(Value):
    def __init__(self, n: ty.Optional[float] = None) -> None:
        self.n = n

    def __repr__(self) -> str:
        return "Float("+repr(self.n)+")"


def __create_binop_float(
        op: ty.Callable[[float, ty.Any], ty.Any],
) -> ty.Callable:
    def binop(self: Float,
              other: Value,
              src_pos: ty.Optional[Pos] = None
              ) -> ty.Union[Float, 'NotImplemented']:
        if isinstance(other, (Int, Float)):
            if self.n is None or other.n is None:
                return Float()

            try:
                new_n = op(self.n, other.n)  # type: ty.Optional[int]
            except ZeroDivisionError:
                new_n = None
            except ValueError:
                new_n = None
            except OverflowError:
                new_n = None

            if isinstance(new_n, float) or new_n is None:
                return Float(new_n)
            else:
                return Any()
        return NotImplemented
    return binop


for op in BINARY_OP_METHODS:
    if hasattr(float, op):
        setattr(Float, op, __create_binop_float(getattr(float, op)))

binop_rules.extractRulesFromClass(Float)


class ValueAsWithStmt(object):
    value = None  # type: Int

    def __init__(self, val: 'Int') -> None:
        self.value = val

    def __enter__(self):
        # type: (...) -> Int
        return self.value

    def __exit__(self, exc_type, exc_value, traceback  # type: ignore
                 ) -> None:
        pass


def for_loop(iterable: Iterable) -> ValueAsWithStmt:
    # extracting type the elements in the iterable value
    # type_elems = iterable.type_.__args__[0].__args__[0] # type: ignore
    return ValueAsWithStmt(Int(None))
