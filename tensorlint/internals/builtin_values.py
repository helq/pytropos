import typing as ty

from .value import Value, Any
from .rules import binop_rules

__all__ = ['Int', 'Iterable', 'Float', 'ValueAsWithStmt', 'for_loop']

Pos = ty.Tuple[int, int]


class Iterable(Value):
    val = None  # type: ty.Any

    def __init__(self, val: ty.Any) -> None:
        self.val = val


class Str(Value):
    def __init__(self, s: ty.Optional[str] = None) -> None:
        self.s = s

    def unite_inside(self, other: Value) -> Value:
        assert type(other) is Str, \
            "Sorry, but I only unite with other Strs"
        return Str()


def _Int_op_output_is_int(
        op: ty.Callable[[int, int], int]
) -> ty.Callable[['Int', Value, ty.Optional[Pos]], ty.Union['Int', 'NotImplemented']]:

    def binop(
            me: 'Int',
            other: Value,
            src_pos: ty.Optional[Pos] = None
    ) -> ty.Union['Int', 'NotImplemented']:
        if isinstance(other, Int):
            if me.n is None or other.n is None:
                return Int()
            try:
                new_n = op(me.n, other.n)  # type: ty.Optional[int]
            except ZeroDivisionError:
                # TODO(helq): add warning to list of warnings
                new_n = None
            except ValueError:  # This only happens with rshift and lshift
                new_n = None
            return Int(new_n)
        return NotImplemented

    return binop


def _Int_op_output_is_float(
        op: ty.Callable[[int, int], float]
) -> ty.Callable[['Int', Value, ty.Optional[Pos]], ty.Union['Float', 'NotImplemented']]:

    def binop(
            me: 'Int',
            other: Value,
            src_pos: ty.Optional[Pos] = None
    ) -> ty.Union['Float', 'NotImplemented']:
        if isinstance(other, Int):
            if me.n is None or other.n is None:
                return Float()
            try:
                new_n = op(me.n, other.n)  # type: ty.Optional[float]
            except ZeroDivisionError:
                new_n = None
            return Float(new_n)
        return NotImplemented

    return binop


def _Int_op_output_is_any(
        op: ty.Callable[[int, int], ty.Union[float, int]]
) -> ty.Callable[['Int', Value, ty.Optional[Pos]], ty.Union['Float', 'NotImplemented']]:

    def binop(
            me: 'Int',
            other: Value,
            src_pos: ty.Optional[Pos] = None
    ) -> ty.Union['Float', 'NotImplemented']:
        if isinstance(other, Int):
            if me.n is None or other.n is None:
                return Any()
            try:
                new_n = op(me.n, other.n)  # type: ty.Union[int, float, None]
            except ZeroDivisionError:
                new_n = None

            if isinstance(new_n, int):
                return Int(new_n)
            elif isinstance(new_n, float):
                return Float(new_n)
            return Any()
        return NotImplemented

    return binop


# TODO(helq): trying to set an attribute should throw an error (ie, the
# simulation of the basic building blocks (int, float, ...) should be as close
# as possible to the official libraries)
@binop_rules.extractRulesFromClass
class Int(Value):
    def __init__(self, n: ty.Optional[int] = None) -> None:
        assert n is None or isinstance(n, int), \
            "Int can only carry int numbers (or None). It was given `{}`".format(type(n))
        self.n = n

    def unite_inside(self, other: Value) -> Value:
        assert type(other) is Int, \
            "Sorry, but I only unite with other Ints"
        if self.n == other.n:  # type: ignore
            return Int(self.n)
        return Int()

    def __repr__(self) -> str:
        return "Int("+repr(self.n)+")"

    # TODO(helq): add test to make sure all dunder methods from int are implemented
    add_op       = _Int_op_output_is_int(int.__add__)
    radd_op      = _Int_op_output_is_int(int.__radd__)
    sub_op       = _Int_op_output_is_int(int.__sub__)
    rsub_op      = _Int_op_output_is_int(int.__rsub__)
    mul_op       = _Int_op_output_is_int(int.__mul__)
    rmul_op      = _Int_op_output_is_int(int.__rmul__)
    truediv_op   = _Int_op_output_is_float(int.__truediv__)
    rtruediv_op  = _Int_op_output_is_float(int.__rtruediv__)
    floordiv_op  = _Int_op_output_is_int(int.__floordiv__)
    rfloordiv_op = _Int_op_output_is_int(int.__rfloordiv__)
    mod_op       = _Int_op_output_is_int(int.__mod__)
    rmod_op      = _Int_op_output_is_int(int.__rmod__)
    pow_op       = _Int_op_output_is_any(int.__pow__)
    rpow_op      = _Int_op_output_is_any(int.__rpow__)
    lshift_op    = _Int_op_output_is_int(int.__lshift__)
    rlshift_op   = _Int_op_output_is_int(int.__rlshift__)
    rshift_op    = _Int_op_output_is_int(int.__rshift__)
    rrshift_op   = _Int_op_output_is_int(int.__rrshift__)


def _Float_op_output_is_float(
        op: ty.Callable[[float, ty.Union[float, int]], float]
) -> ty.Callable[['Float', Value, ty.Optional[Pos]], ty.Union['Float', 'NotImplemented']]:

    def binop(
            me: 'Float',
            other: Value,
            src_pos: ty.Optional[Pos] = None
    ) -> ty.Union['Float', 'NotImplemented']:
        if isinstance(other, (Float, Int)):
            if me.n is None or other.n is None:
                return Float()
            try:
                new_n = op(me.n, other.n)  # type: ty.Optional[float]
            except ZeroDivisionError:
                # TODO(helq): add warning
                new_n = None

            return Float(new_n)
        return NotImplemented

    return binop


def _Float_op_output_is_any(
        op: ty.Callable[[float, ty.Union[float, int]], ty.Union[float, complex]]
) -> ty.Callable[['Float', Value, ty.Optional[Pos]], ty.Union['Float', 'NotImplemented']]:

    def binop(
            me: 'Float',
            other: Value,
            src_pos: ty.Optional[Pos] = None
    ) -> ty.Union['Float', 'NotImplemented']:
        if isinstance(other, (Float, Int)):
            if me.n is None or other.n is None:
                return Any()
            try:
                new_n = op(me.n, other.n)  # type: ty.Union[float, int, complex, None]
            except ZeroDivisionError:
                # TODO(helq): add warning
                new_n = None

            if isinstance(new_n, int):
                return Int(new_n)
            if isinstance(new_n, float):
                return Float(new_n)
            return Any()
        return NotImplemented

    return binop


# TODO(helq): add warning when operating with nan values
@binop_rules.extractRulesFromClass
class Float(Value):
    def __init__(self, n: ty.Optional[float] = None) -> None:
        assert n is None or isinstance(n, float), \
            "Float can only carry float numbers (or None). It was given `{}`".format(type(n))
        self.n = n

    def unite_inside(self, other: Value) -> Value:
        assert type(other) is Float, \
            "Sorry, but I only unite with other Floats"
        if self.n == other.n:  # type: ignore
            return Float(self.n)
        return Float()

    def __repr__(self) -> str:
        return "Float("+repr(self.n)+")"

    add_op       = _Float_op_output_is_float(float.__add__)
    radd_op      = _Float_op_output_is_float(float.__radd__)
    sub_op       = _Float_op_output_is_float(float.__sub__)
    rsub_op      = _Float_op_output_is_float(float.__rsub__)
    mul_op       = _Float_op_output_is_float(float.__mul__)
    rmul_op      = _Float_op_output_is_float(float.__rmul__)
    truediv_op   = _Float_op_output_is_float(float.__truediv__)
    rtruediv_op  = _Float_op_output_is_float(float.__rtruediv__)
    floordiv_op  = _Float_op_output_is_float(float.__floordiv__)
    rfloordiv_op = _Float_op_output_is_float(float.__rfloordiv__)
    mod_op       = _Float_op_output_is_float(float.__mod__)
    rmod_op      = _Float_op_output_is_float(float.__rmod__)
    pow_op       = _Float_op_output_is_any(float.__pow__)
    rpow_op      = _Float_op_output_is_any(float.__rpow__)


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
