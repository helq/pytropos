import re
from functools import partial
from abc import abstractmethod
from typing import Tuple, Optional, Any, Union

from ..abstract_domain import AbstractDomain
from ..errors import TypeCheckLogger

from ..tools import Pos

__all__ = ['AbstractValue', 'Int', 'Float']


ops_symbols = {
    'add': '+',
    'sub': '+',
    'mul': '*',
    'truediv': '/',
    'floordiv': '//',
    'mod': '%',
    # 'divmod': 'divmod',
    # 'pow': '**',
    'lshift': '<<',
    'rshift': '>>',
    # 'and': '&',
    # 'xor': '^',
    # 'or': '|',
}

extract_op = re.compile(r'op_([a-zA-Z]*)(_([a-zA-Z]*))?$')


# TODO(helq): add `get` method to simulate access to member values like, num.some.var
class AbstractValue(AbstractDomain):
    """
    All variables in pytropos must derivate from `AbstractValue`. `AbstractValue` is just
    like `object` for all objects in python.
    """

    @abstractmethod
    def join(self, other: Any) -> Any:
        """Returns the new value that captures the other two (self and other)"""
        raise NotImplementedError()

    @property
    @abstractmethod
    def type_name(self) -> str:
        raise NotImplementedError()

    @property
    @abstractmethod
    def abstract_repr(self) -> str:
        raise NotImplementedError()

    def fun_call(self,
                 args: Tuple[Any],
                 vau: Any,
                 src_pos: Optional[Pos]
                 ) -> Any:
        """The Abstract Value is invoked as a function"""
        raise NotImplementedError()

    def call_getitem(self, key: Any) -> Any:
        """Invoking Abstract Value's __getitem__"""
        raise NotImplementedError()

    def call_setitem(self, key: Any, val: Any) -> Any:
        """Invoking Abstract Value's __getitem__"""
        raise NotImplementedError()

    def op_OP(self, other: Any, pos: Optional[Pos]) -> Any:
        """
        This operation defines how to OPERATE two values of the same type.

        For example, op_add defines how to add two values, and op_mul defines how to
        multiplicate two values.

        To define how to add to another values that are of a different type use:
        - op_add_TYPE
        - op_radd_TYPE

        where TYPE is the type of the value, e.g.,
        op_add_Int, and op_radd_Int
        """
        raise NotImplementedError()

    op_add = op_OP
    op_mul = op_OP
    op_sub = op_OP
    op_truediv = op_OP
    op_floordiv = op_OP
    op_mod = op_OP
    op_lshift = op_OP
    op_rshift = op_OP


class Int(AbstractValue):
    """Int Abstract Domain. It is the simplest, the abstraction function is Int(n) and
    the concretisation is all naturals for n==None and {n} for n"""
    def __init__(self, val: Optional[int] = None) -> None:
        """
        If val is None, then the Int value is Top
        """
        self.val = val

    __top = None  # type: Int

    @classmethod
    def top(cls) -> 'Int':
        """The top value of this Abstract Domain is Int(None)"""
        if cls.__top is None:
            cls.__top = Int(None)
        return cls.__top

    def is_top(self) -> bool:
        return self.val is None

    def join(self, other: 'Int') -> 'Int':
        if self.val == other.val:
            return self
        return Int()

    @property
    def type_name(self) -> str:
        return "int"

    @property
    def abstract_repr(self) -> str:
        if self.val is None:
            return "int?"
        else:
            return repr(self.val)

    def __getattribute__(self, name: str) -> Any:
        # Checking if name is 'op_OP' (eg, 'op_add')
        op = extract_op.match(name)
        if op and (
            not op[3]  # allowing op_add
            or op[3] in ('Int', 'Bool')  # allowing op_add_Bool
        ):
            if op[1] in ('add', 'sub', 'mul', 'radd', 'rsub', 'rmul'):
                return partial(Int._Int__operate, self, op[1])  # type: ignore
            if op[1] in ('lshift', 'rshift', 'rlshift', 'rrshift'):
                return partial(Int._Int__operate_shift, self, op[1])  # type: ignore
            if op[1] in ('truediv', 'floordiv', 'mod', 'rtruediv', 'rfloordiv', 'rmod'):
                return partial(Int._Int__operate_div, self, op[1])  # type: ignore

        return object.__getattribute__(self, name)

    def __operate(self, op: str, other: 'Int', pos: Optional[Pos]) -> 'Int':
        if self.val is None or other.val is None:
            return Int.top()

        new_val = getattr(int, f"__{op}__")(self.val, other.val)
        return Int(new_val)

    def __operate_shift(self, op: str, other: 'Int', pos: Optional[Pos]) -> 'Int':
        if self.val is None or other.val is None:
            return Int.top()

        try:
            new_val = getattr(int, f"__{op}__")(self.val, other.val)
        except ValueError as msg:
            TypeCheckLogger().new_warning(
                "E002", f"ValueError: {msg}", pos)
            return Int.top()

        return Int(new_val)

    def __operate_div(self,
                      op: str,
                      other: 'Int',
                      pos: Optional[Pos]) -> Union['Int', 'Float', None]:
        if self.val is None or other.val is None:
            return None

        try:
            new_val = getattr(int, f"__{op}__")(self.val, other.val)
        except ZeroDivisionError as msg:
            TypeCheckLogger().new_warning(
                "E001", f"ZeroDivisionError: {msg}", pos)
            return None

        return Int(new_val) if isinstance(new_val, int) else Float(new_val)


class Float(AbstractValue):
    """Float Abstract Domain. It is the simplest, the abstraction function is Float(n) and
    the concretisation is floating numbers for n==None and {n} for n"""
    def __init__(self, val: Optional[float] = None) -> None:
        """
        If val is None, then the Float value is Top
        """
        self.val = val

    __top = None  # type: Float

    @classmethod
    def top(cls) -> 'Float':
        """The top value of this Abstract Domain is Float(None)"""
        if cls.__top is None:
            cls.__top = Float(None)
        return cls.__top

    def is_top(self) -> bool:
        return self.val is None

    def join(self, other: 'Float') -> 'Float':
        if self.val == other.val:
            return self
        return Float()

    @property
    def type_name(self) -> str:
        return "float"

    @property
    def abstract_repr(self) -> str:
        if self.val is None:
            return "float?"
        else:
            return repr(self.val)

    def __getattribute__(self, name: str) -> Any:
        # Checking if name is 'op_OP' (eg, 'op_add')
        op = extract_op.match(name)
        if op and (
                op[3] is None or  # Allowing op_add
                op[3] in ('Int', 'Bool')  # Allowing op_add_Int
        ):
            if op[1] in ('add', 'sub', 'mul', 'radd', 'rsub', 'rmul'):
                return partial(object.__getattribute__(self, '_Float__operate'), op[1])
            if op[1] in ('truediv', 'floordiv', 'mod', 'rtruediv', 'rfloordiv', 'rmod'):
                return partial(object.__getattribute__(self, '_Float__operate_float'), op[1])
            if op[1] in ('rshift', 'lshift', 'rrshift', 'rlshift'):
                return partial(object.__getattribute__(self, '_Float__operate_any'), op[1])

        return object.__getattribute__(self, name)

    def __operate(self, op: str, other: 'Union[Float, Int]', pos: Optional[Pos]) -> 'Float':
        if self.val is None or other.val is None:
            return Float.top()

        new_val = getattr(float, f'__{op}__')(self.val, other.val)
        return Float(new_val)

    def __operate_float(self,
                        op: str,
                        other: 'Union[Float, Int]',
                        pos: Optional[Pos]) -> 'Float':
        if self.val is None or other.val is None:
            return Float.top()

        try:
            new_val = getattr(float, f'__{op}__')(self.val, other.val)
        except ZeroDivisionError as msg:
            TypeCheckLogger().new_warning(
                "E001", f"ZeroDivisionError: {msg}", pos)
            return Float.top()

        return Float(new_val)

    def __operate_any(self,
                      op: str,
                      other: 'Union[Float, Int]',
                      pos: Optional[Pos]) -> Union['Float', 'Int', None]:
        if self.val is None or other.val is None:
            return None

        try:
            new_val = getattr(float, f'__{op}__')(self.val, other.val)
        except ZeroDivisionError as msg:
            new_val = None
            TypeCheckLogger().new_warning("E001", "ZeroDivisionError: " + str(msg), pos)
        except OverflowError as msg:
            new_val = None
            TypeCheckLogger().new_warning("E003", "OverflowError: " + str(msg), pos)

        if isinstance(new_val, int):
            return Int(new_val)
        if isinstance(new_val, float):
            return Float(new_val)
        if new_val is not None:
            TypeCheckLogger().new_warning(
                "W001",
                "Weird return value: I expected an int or float from operating {} with "
                "{} but got a {} instead".format(self.val, other.val, type(new_val)),
                pos)

        return None


class Bool(AbstractValue):
    r"""
    Bool Abstract Domain.
             Top
            /   \
          True False
            \   /
            Bottom  <  this isn't implemented
    """
    def __init__(self, val: Optional[bool] = None) -> None:
        """
        If val is None, then the Bool value is Top
        """
        self.val = val

    __top = None  # type: Bool

    @classmethod
    def top(cls) -> 'Bool':
        """The top value of this Abstract Domain is Bool(None)"""
        if cls.__top is None:
            cls.__top = Bool(None)
        return cls.__top

    def is_top(self) -> bool:
        return self.val is None

    def join(self, other: 'Bool') -> 'Bool':
        if self.val is other.val:
            return self
        return Bool()

    @property
    def type_name(self) -> str:
        return "bool"

    @property
    def abstract_repr(self) -> str:
        if self.val is None:
            return "bool?"
        else:
            return repr(self.val)

    __getattribute__ = Int.__getattribute__
