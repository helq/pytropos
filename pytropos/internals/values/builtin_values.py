import typing as ty

import math

from .base import AbstractValue, Any
from ..operations.base import add_ops_to_global
from ..tools import Pos
from ..errors import TypeCheckLogger

__all__ = ['Int', 'Float', 'Bool', 'Str', 'Iterable', 'ValueAsWithStmt', 'for_loop']


class Iterable(AbstractValue):
    def __init__(self, val: AbstractValue) -> None:
        # check all its internal values are None (Int(None), or Float(None))
        self.val = val

    def next(self) -> AbstractValue:
        return self.val

    def join(self, other: 'AbstractValue') -> 'AbstractValue':
        raise NotImplementedError()

    def congruent_inside(self, other: 'AbstractValue') -> bool:
        raise NotImplementedError()

    @property
    def type_name(self) -> str:
        raise NotImplementedError()

    @property
    def abstract_repr(self) -> str:
        raise NotImplementedError()


class Str(AbstractValue):
    def __init__(self, s: ty.Optional[str] = None) -> None:
        self.s = s

    def join(self, other: AbstractValue) -> AbstractValue:
        assert type(other) is Str, \
            "Sorry, but I only unite with other Strs"
        return Str()

    def congruent_inside(self, other: 'AbstractValue') -> bool:
        assert type(other) is Str, \
            "Sorry, but I only unite with other Strs"
        return True

    @property
    def type_name(self) -> str:
        return "str"

    @property
    def abstract_repr(self) -> str:
        if self.s is None:
            return "str?"
        else:
            return repr(self.s)


def _Int_op_output_is_int(
        op: ty.Callable[[int, int], int]
) -> ty.Callable[['Int', AbstractValue, ty.Optional[Pos]], ty.Union['Int', 'NotImplemented']]:

    def binop(
            me: 'Int',
            other: AbstractValue,
            src_pos: ty.Optional[Pos] = None
    ) -> ty.Union['Int', 'NotImplemented']:
        if isinstance(other, Int):
            if me.n is None or other.n is None:
                return Int()
            try:
                new_n = op(me.n, other.n)  # type: ty.Optional[int]
            except ZeroDivisionError as msg:
                new_n = None
                TypeCheckLogger().new_warning("E001", "ZeroDivisionError: " + str(msg), src_pos)
            except ValueError as msg:  # This only happens with rshift and lshift
                new_n = None
                TypeCheckLogger().new_warning("E002", "ValueError: " + str(msg), src_pos)
            return Int(new_n)
        return NotImplemented

    return binop


def _Int_op_output_is_float(
        op: ty.Callable[[int, int], float]
) -> ty.Callable[['Int', AbstractValue, ty.Optional[Pos]], ty.Union['Float', 'NotImplemented']]:

    def binop(
            me: 'Int',
            other: AbstractValue,
            src_pos: ty.Optional[Pos] = None
    ) -> ty.Union['Float', 'NotImplemented']:
        if isinstance(other, Int):
            if me.n is None or other.n is None:
                return Float()
            try:
                new_n = op(me.n, other.n)  # type: ty.Optional[float]
            except ZeroDivisionError as msg:
                new_n = None
                TypeCheckLogger().new_warning("E001", "ZeroDivisionError: " + str(msg), src_pos)
            return Float(new_n)
        return NotImplemented

    return binop


def _Int_op_output_is_any(
        op: ty.Callable[[int, int], ty.Union[float, int]]
) -> ty.Callable[['Int', AbstractValue, ty.Optional[Pos]], ty.Union['Float', 'NotImplemented']]:

    def binop(
            me: 'Int',
            other: AbstractValue,
            src_pos: ty.Optional[Pos] = None
    ) -> ty.Union['Float', 'NotImplemented']:
        if isinstance(other, Int):
            if me.n is None or other.n is None:
                return Any()
            try:
                new_n = op(me.n, other.n)  # type: ty.Union[int, float, None]
            except ZeroDivisionError as msg:
                new_n = None
                TypeCheckLogger().new_warning("E001", "ZeroDivisionError: " + str(msg), src_pos)

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
@add_ops_to_global
class Int(AbstractValue):
    def __init__(self, n: ty.Optional[int] = None) -> None:
        assert n is None or isinstance(n, int), \
            "Int can only carry int numbers (or None). It was given `{}`".format(type(n))
        self.n = n

    def join(self, other: AbstractValue) -> AbstractValue:
        assert type(other) is Int, \
            "Sorry, but I only unite with other Ints"
        if self.n == other.n:  # type: ignore
            return Int(self.n)
        return Int()

    def congruent_inside(self, other: 'AbstractValue') -> bool:
        assert isinstance(other, Int) and type(other) is Int, \
            "Sorry, but I only unite with other Ints"
        return self.n is None \
            or other.n is None \
            or self.n == other.n

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

    def bool_op(
            self,
            src_pos: ty.Optional[Pos] = None
    ) -> ty.Union['Bool', 'NotImplemented']:
        if self.n is None:
            return Bool()
        return Bool(bool(self.n))

    def eq_op(
            self,
            other: AbstractValue,
            src_pos: ty.Optional[Pos] = None
    ) -> ty.Union['Bool', 'NotImplemented']:
        if isinstance(other, Int):
            if self.n is None or other.n is None:
                return Bool()
            return Bool(self.n == other.n)
        return NotImplemented

    @property
    def type_name(self) -> str:
        return "int"

    @property
    def abstract_repr(self) -> str:
        if self.n is None:
            return "int?"
        else:
            return repr(self.n)


def _Float_op_output_is_float(
        op: ty.Callable[[float, ty.Union[float, int]], float]
) -> ty.Callable[['Float', AbstractValue, ty.Optional[Pos]], ty.Union['Float', 'NotImplemented']]:

    def binop(
            me: 'Float',
            other: AbstractValue,
            src_pos: ty.Optional[Pos] = None
    ) -> ty.Union['Float', 'NotImplemented']:
        if isinstance(other, (Float, Int)):
            if me.n is None or other.n is None:
                return Float()
            try:
                new_n = op(me.n, other.n)  # type: ty.Optional[float]
            except ZeroDivisionError as msg:
                new_n = None
                TypeCheckLogger().new_warning("E001", "ZeroDivisionError: " + str(msg), src_pos)

            return Float(new_n)
        return NotImplemented

    return binop


def _Float_op_output_is_any(
        op: ty.Callable[[float, ty.Union[float, int]], ty.Union[float, complex]]
) -> ty.Callable[['Float', AbstractValue, ty.Optional[Pos]], ty.Union['Float', 'NotImplemented']]:

    def binop(
            me: 'Float',
            other: AbstractValue,
            src_pos: ty.Optional[Pos] = None
    ) -> ty.Union['Float', 'NotImplemented']:
        if isinstance(other, (Float, Int)):
            if me.n is None or other.n is None:
                return Any()
            try:
                new_n = op(me.n, other.n)  # type: ty.Union[float, int, complex, None]
            except ZeroDivisionError as msg:
                new_n = None
                TypeCheckLogger().new_warning("E001", "ZeroDivisionError: " + str(msg), src_pos)
            except OverflowError as msg:
                new_n = None
                TypeCheckLogger().new_warning("E003", "OverflowError: " + str(msg), src_pos)

            if isinstance(new_n, int):
                return Int(new_n)
            if isinstance(new_n, float):
                return Float(new_n)
            if new_n is not None:
                TypeCheckLogger().new_warning(
                    "W001",
                    "Weird return value: I expected an int or float from operating {} with "
                    "{} but got a {} instead".format(me.n, other.n, type(new_n)),
                    src_pos)

            return Any()

        return NotImplemented

    return binop


# TODO(helq): add warning when operating with nan values
@add_ops_to_global
class Float(AbstractValue):
    def __init__(self, n: ty.Optional[float] = None) -> None:
        assert n is None or isinstance(n, float), \
            "Float can only carry float numbers (or None). It was given `{}`".format(type(n))
        self.n = n

    def join(self, other: AbstractValue) -> AbstractValue:
        assert type(other) is Float, \
            "Sorry, but I only unite with other Floats"
        if self.n == other.n:  # type: ignore
            return Float(self.n)
        return Float()

    def congruent_inside(self, other: 'AbstractValue') -> bool:
        assert isinstance(other, Float) and type(other) is Float, \
            "Sorry, but I only unite with other Floats"
        return self.n is None \
            or other.n is None \
            or (math.isnan(self.n) and math.isnan(other.n)) \
            or (math.isinf(self.n) and math.isinf(other.n)) \
            or self.n == other.n

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

    def bool_op(
            self,
            src_pos: ty.Optional[Pos] = None
    ) -> ty.Union['Bool', 'NotImplemented']:
        if self.n is None:
            return Bool()
        return Bool(bool(self.n))

    def eq_op(
            self,
            other: AbstractValue,
            src_pos: ty.Optional[Pos] = None
    ) -> ty.Union['Bool', 'NotImplemented']:
        if isinstance(other, (Int, Float)):
            if self.n is None or other.n is None:
                return Bool()
            return Bool(self.n == other.n)
        return NotImplemented

    @property
    def type_name(self) -> str:
        return "float"

    @property
    def abstract_repr(self) -> str:
        if self.n is None:
            return "float?"
        else:
            return repr(self.n)


@add_ops_to_global
class Bool(Int):
    def __init__(self, n: ty.Optional[bool] = None) -> None:
        assert n is None or isinstance(n, bool), \
            "Bool can only carry bools numbers (or None). It was given `{}`".format(type(n))
        self.n = n

    def __repr__(self) -> str:
        return "Bool("+repr(self.n)+")"

    def join(self, other: AbstractValue) -> AbstractValue:
        assert type(other) is Bool, \
            "Sorry, but I only unite with other Bool"
        if self.n == other.n:  # type: ignore
            return Bool(self.n)  # type: ignore
        return Bool()

    def congruent_inside(self, other: 'AbstractValue') -> bool:
        assert isinstance(other, Bool) and type(other) is Bool, \
            "Sorry, but I only unite with other Bools"
        return self.n is None \
            or other.n is None \
            or self.n == other.n

    def bool_op(
            self,
            src_pos: ty.Optional[Pos] = None
    ) -> ty.Union['Bool', 'NotImplemented']:
        return self

    @property
    def type_name(self) -> str:
        return "bool"

    @property
    def abstract_repr(self) -> str:
        if self.n is None:
            return "bool?"
        else:
            return repr(self.n)


# TODO(helq): THIS SHOULDN'T BE USED!!! kill it!
class ValueAsWithStmt(object):
    def __init__(self, val: AbstractValue) -> None:
        self.value = val

    def __enter__(self):
        # type: (...) -> AbstractValue
        return self.value

    def __exit__(self, exc_type, exc_value, traceback  # type: ignore
                 ) -> None:
        pass


# TODO(helq): THIS SHOULDN'T BE USED!!! kill it!
def for_loop(iterable: Iterable) -> ValueAsWithStmt:
    # extracting type the elements in the iterable value
    # type_elems = iterable.type_.__args__[0].__args__[0] # type: ignore
    return ValueAsWithStmt(iterable.next())
