import re
from functools import partial
from typing import Optional, Any, Union

from .abstract_value import AbstractValue
from ..errors import TypeCheckLogger
from ..miscelaneous import Pos

__all__ = ['Int', 'Float', 'Bool', 'NoneType']


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

    'lt': '<',
    'le': '<=',
    'gt': '>',
    'ge': '>=',
}

extract_op = re.compile(r'op_([a-zA-Z]*)(_([a-zA-Z]*))?$')


class Int(AbstractValue):
    """Int Abstract Domain. It is the simplest abstract domain for Numbers.

    The abstraction function is Int(n) and the concretisation is all naturals for n==None
    and {n} for n
    """
    def __init__(self, val: Optional[int] = None) -> None:
        """
        If val is None, then the Int value is Top
        """
        self.val = val

    def __repr__(self) -> str:
        return f"Int({self.val})"

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

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Int):
            return False
        if self.is_top() and other.is_top():
            return True
        return self.val == other.val

    _int_to_int_ops = {'add', 'sub', 'mul', 'radd', 'rsub', 'rmul'}
    _int_to_bool_ops = {'eq', 'ne', 'lt', 'le', 'gt', 'ge'}
    _int_to_int_ops_shift = {'lshift', 'rshift', 'rlshift', 'rrshift'}
    _int_to_int_ops_div = {'truediv', 'floordiv', 'mod', 'rtruediv', 'rfloordiv', 'rmod'}

    def __getattribute__(self, name: str) -> Any:
        # Checking if name is 'op_OP' (eg, 'op_add')
        op = extract_op.match(name)
        if op and (
            not op[3]  # allowing op_add
            or op[3] in ('Int', 'Bool')  # allowing op_add_Bool
        ):
            if op[1] in Int._int_to_int_ops:
                return partial(Int.__operate_int_to_int, self, op[1])
            if op[1] in Int._int_to_bool_ops:
                return partial(Int.__operate_int_to_bool, self, op[1])
            if op[1] in Int._int_to_int_ops_shift:
                return partial(Int.__operate_int_to_int_shift, self, op[1])
            if op[1] in Int._int_to_int_ops_div:
                return partial(Int.__operate_int_div, self, op[1])

        return object.__getattribute__(self, name)

    def __operate_int_to_int(self, op: str, other: 'Int', pos: Optional[Pos]) -> 'Int':
        if self.val is None or other.val is None:
            return Int.top()

        new_val = getattr(int, f"__{op}__")(self.val, other.val)
        return Int(new_val)

    def __operate_int_to_bool(self, op: str, other: 'Int', pos: Optional[Pos]) -> 'Bool':
        if self.val is None or other.val is None:
            return Bool.top()

        new_val = getattr(int, f"__{op}__")(self.val, other.val)
        return Bool(new_val)

    def __operate_int_to_int_shift(self, op: str, other: 'Int', pos: Optional[Pos]) -> 'Int':
        if self.val is None or other.val is None:
            return Int.top()

        try:
            new_val = getattr(int, f"__{op}__")(self.val, other.val)
        except ValueError as msg:
            TypeCheckLogger().new_warning(
                "E002", f"ValueError: {msg}", pos)
            return Int.top()

        return Int(new_val)

    def __operate_int_div(
            self,
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

    def op_bool(self, pos: Optional[Pos]) -> 'Bool':
        if self.is_top():
            return Bool.top()
        else:
            return Bool(bool(self.val))


class Float(AbstractValue):
    """Float Abstract Domain. It is the simplest abstract domain for numbers.

    The abstraction function is Float(n) and the concretisation is floating numbers for
    n==None and {n} for n
    """
    def __init__(self, val: Optional[float] = None) -> None:
        """
        If val is None, then the Float value is Top
        """
        self.val = val

    def __repr__(self) -> str:
        return f"Float({self.val})"

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

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Float):
            return False
        if self.is_top() and other.is_top():
            return True
        return self.val == other.val

    _to_floats_ops = set(['add', 'sub', 'mul', 'radd', 'rsub', 'rmul'])
    _to_bools_ops = set(['eq', 'ne', 'lt', 'le', 'gt', 'ge'])
    _to_floats_div_ops = set(['truediv', 'floordiv', 'mod', 'rtruediv', 'rfloordiv', 'rmod'])
    _to_any_shift_ops = set(['rshift', 'lshift', 'rrshift', 'rlshift'])

    def __getattribute__(self, name: str) -> Any:
        # Checking if name is 'op_OP' (eg, 'op_add')
        op = extract_op.match(name)
        if op and (
                op[3] is None or  # Allowing op_add
                op[3] in ('Int', 'Bool')  # Allowing op_add_Int
        ):
            if op[1] in self._to_floats_ops:
                return partial(Float.__operate_to_floats, self, op[1])
            if op[1] in self._to_bools_ops:
                return partial(Float.__operate_to_bools, self, op[1])
            if op[1] in self._to_floats_div_ops:
                return partial(Float.__operate_to_floats_div, self, op[1])
            if op[1] in self._to_any_shift_ops:
                return partial(Float.__operate_to_any, self, op[1])

        return object.__getattribute__(self, name)

    def __operate_to_floats(
            self,
            op: str,
            other: 'Union[Float, Int]',
            pos: Optional[Pos]
    ) -> 'Float':
        if self.val is None or other.val is None:
            return Float.top()

        new_val = getattr(float, f'__{op}__')(self.val, other.val)
        return Float(new_val)

    def __operate_to_bools(
            self,
            op: str,
            other: 'Union[Float, Int]',
            pos: Optional[Pos]
    ) -> 'Bool':
        if self.val is None or other.val is None:
            return Bool.top()

        new_val = getattr(float, f'__{op}__')(self.val, other.val)
        return Bool(new_val)

    def __operate_to_floats_div(
            self,
            op: str,
            other: 'Union[Float, Int]',
            pos: Optional[Pos]
    ) -> 'Float':
        if self.val is None or other.val is None:
            return Float.top()

        try:
            new_val = getattr(float, f'__{op}__')(self.val, other.val)
        except ZeroDivisionError as msg:
            TypeCheckLogger().new_warning(
                "E001", f"ZeroDivisionError: {msg}", pos)
            return Float.top()

        return Float(new_val)

    def __operate_to_any(
            self,
            op: str,
            other: 'Union[Float, Int]',
            pos: Optional[Pos]
    ) -> 'Union[Float, Int, None]':
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

    def op_bool(self, pos: Optional[Pos]) -> 'Bool':
        if self.is_top():
            return Bool.top()
        else:
            return Bool(bool(self.val))


class Bool(AbstractValue):
    r"""Bool Abstract Domain.

    ::

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

    def __repr__(self) -> str:
        return f"Bool({self.val})"

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

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Bool):
            return False
        if self.is_top() and other.is_top():
            return True
        return self.val == other.val

    __getattribute__ = Int.__getattribute__

    def op_bool(self, pos: Optional[Pos]) -> 'Bool':
        return self


class NoneType(AbstractValue):
    "None Abstract Domain. It's composed of a single Value: None"

    __instance = None  # type: NoneType

    def __new__(cls) -> 'NoneType':
        "Making sure only one object is ever created"
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance

    def __repr__(self) -> str:
        return f"NoneType()"

    @classmethod
    def top(cls) -> 'NoneType':
        """The top value of this Abstract Domain"""
        return cls()

    def is_top(self) -> bool:
        return True

    def join(self, other: 'NoneType') -> 'NoneType':
        return self

    @property
    def type_name(self) -> str:
        return "NoneType"

    @property
    def abstract_repr(self) -> str:
        return "None"

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, NoneType):
            return True
        return False

    def __getattribute__(self, name: str) -> Any:
        # Checking if name is 'op_OP' (eg, 'op_add')
        op = extract_op.match(name)

        if op and (
                op[1] == 'ne' or  # None.ne(None) => False
                (op[1] == 'eq' and op[3] in ('Int', 'Bool', 'Float'))  # None.ne(5) => False
        ):
            return partial(NoneType.__operate_ret_false, self)

        return object.__getattribute__(self, name)

    # def op_eq(self, other: 'NoneType', pos: Optional[Pos]) -> 'Bool':  # type: ignore
    #     return Bool(True)

    def __operate_ret_false(
            self,
            other: AbstractValue,
            pos: Optional[Pos]) -> Bool:
        return Bool(False)

    def op_bool(self, pos: Optional[Pos]) -> 'Bool':
        return Bool(False)
