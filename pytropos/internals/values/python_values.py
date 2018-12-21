from enum import Enum
from functools import partial
from typing import Union, Optional, Any

from .primitive_values import Int, Float, Bool, AbstractValue, ops_symbols
from ..abstract_domain import AbstractDomain
from ..errors import TypeCheckLogger

from ..tools import Pos


__all__ = ['PythonValue', 'PT']


class PT(Enum):
    """Python types supported in pytropos"""
    Undefined = 0
    Top = 1
    # Bottom = 2
    # Primitive = 3
    # NoneType = 4
    # IntType = 5
    # BoolType = 6
    # FloatType = 7
    # StrType = 8
    # Function = 9
    # Module = 10
    # UserMadeObject = 11


class PythonValue(AbstractDomain):
    def __init__(self,
                 val: Union[AbstractValue, PT] = PT.Undefined
                 ) -> None:
        self.val = val

    __top = None  # type: PythonValue

    @classmethod
    def top(cls) -> 'PythonValue':
        """Returns the Top element from the lattice: Any?"""
        if cls.__top is None:
            cls.__top = PythonValue(PT.Top)
        return cls.__top

    def is_top(self) -> '__builtins__.bool':
        """Returns True if this object is the top of the lattice, ie, if Any?"""
        return self.val is PT.Top

    def join(self, other: 'PythonValue') -> 'PythonValue':
        raise NotImplementedError()

    def __repr__(self) -> str:
        if self.val is PT.Top:
            return "Top"
        elif self.val is PT.Undefined:
            return "Undefined"
        else:  # self.type is PT.Top
            assert not isinstance(self.val, PT)
            return self.val.abstract_repr

    def __getattr__(self, name: str) -> Any:
        # Checking if name is add, mul, truediv
        if name in ops_symbols.keys():
            return partial(self.operate, name)
        raise AttributeError(f"There is no operation for PythonValues called '{name}'")

    def operate(self, op: str, other: 'PythonValue', pos: Optional[Pos] = None) -> 'PythonValue':
        op_sym = ops_symbols[op]

        if self.val is PT.Top or other.val is PT.Top:
            return PythonValue.top()

        # This assert is always true, it's just to keep Mypy from crying
        assert isinstance(self.val, AbstractValue), \
            f"Left type is {type(self.val)} but should have been an AbstractValue"
        assert isinstance(other.val, AbstractValue), \
            f"Left type is {type(other.val)} but should have been an AbstractValue"

        # If both values have the same type use val.op_add(otherval)
        if type(self.val) is type(other.val):  # noqa: E721
            # Checking if op_add has been overwritten by the class that has been called
            # If it hasn't, the operation result is Top
            op_method = getattr(self.val, f'op_{op}')
            if hasattr(op_method, '__qualname__') and \
               op_method.__qualname__.split('.')[0] == "AbstractValue":
                TypeCheckLogger().new_warning(
                    "E009",
                    f"TypeError: unsupported operand type(s) for {op_sym}: "
                    f"'{self.val.type_name}' and '{other.val.type_name}'",
                    pos)

                newval = PT.Top
            else:
                newval = getattr(self.val, f'op_{op}')(other.val, pos)

        # If values have different type use val.op_add_OtherType(otherval)
        # or otherval.op_add_Type(val)
        else:
            leftOpName = "op_r{op}_{class_name}".format(op=op, class_name=type(self.val).__name__)
            rightOpName = "op_{op}_{class_name}".format(op=op, class_name=type(other.val).__name__)

            try:
                newval = getattr(self.val, rightOpName)(other.val, pos)
            except:  # noqa: E772
                try:
                    newval = getattr(other.val, leftOpName)(self.val, pos)
                except:  # noqa: E772
                    TypeCheckLogger().new_warning(
                        "E009",
                        f"TypeError: unsupported operand type(s) for {op_sym}: "
                        f"'{self.val.type_name}' and '{other.val.type_name}'",
                        pos)

                    newval = PT.Top

        if newval is None:
            return PythonValue.top()
        return PythonValue(newval)


def int(val: Optional['__builtins__.int'] = None) -> PythonValue:
    """Returns an Int wrapped into a PythonValue"""
    return PythonValue(Int(val))


def float(val: Optional['__builtins__.float'] = None) -> PythonValue:
    """Returns an Float wrapped into a PythonValue"""
    return PythonValue(Float(val))


def bool(val: Optional['__builtins__.bool'] = None) -> PythonValue:
    """Returns an Float wrapped into a PythonValue"""
    return PythonValue(Bool(val))


if __name__ == '__main__':
    val1 = PythonValue.top()
    val2 = int()
    val3 = int(2)
    val4 = int(3)
    print(f"{val1} + {val2} == {val1.add(val2)}")
    print(f"{val1} + {val3} == {val1.add(val3)}")
    print(f"{val2} + {val3} == {val2.add(val3)}")
    print(f"{val3} + {val4} == {val3.add(val4)}")
    print(f"{val3} * {val4} == {val3.mul(val4)}")

    val2 = float()
    val3 = float(0.0)
    val4 = float(3.0)
    val5 = val3.floordiv(val3)
    print(f"{val1} + {val2} == {val1.add(val2)}")
    print(f"{val1} + {val3} == {val1.add(val3)}")
    print(f"{val2} + {val3} == {val2.add(val3)}")
    print(f"{val3} + {val4} == {val3.add(val4)}")
    print(f"{val3} * {val4} == {val3.mul(val4)}")
    print(f"{val3} / {val3} == {val3.truediv(val3)}")
    print(f"{val3} // {val3} == {val5}")
    print(f"{val5}.is_top() == {val5.is_top()}")

    val1 = int(0)
    val2 = float(1.0)
    print(f"{val1} / {val2} == {val1.truediv(val2)}")

    val1 = bool(True)
    val2 = int()
    print(f"{val1} + {val2} == {val1.add(val2)}")

    val1 = bool(True)
    val2 = bool(True)
    print(f"{val1} + {val2} == {val1.add(val2)}")

    val1 = bool(True)
    val2 = int()
    print(f"{val1} << {val2} == {val1.lshift(val2)}")

    print(f"Errors: {TypeCheckLogger()}")
