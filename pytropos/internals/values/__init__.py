from typing import Any, TYPE_CHECKING
from typing import Optional  # noqa: F401

from .python_values.python_values import PythonValue
from .python_values.builtin_mutvalues import List, Tuple
from .python_values import Args
from .builtin_values import Int, Float, Bool, NoneType
from .python_values.wrappers import BuiltinModule

__all__ = ['int', 'float', 'bool', 'none', 'list', 'tuple', 'Args', 'Top', 'ModuleTop']


if TYPE_CHECKING:
    from typing import (  # noqa: F401
        Callable, Tuple as Tuple_, Dict, List as List_, Set, Type
    )

    b_int = __builtins__.int
    b_bool = __builtins__.bool
    b_float = __builtins__.float


def int(val: 'Optional[b_int]' = None) -> PythonValue:
    """Returns an Int wrapped into a PythonValue"""
    return PythonValue(Int(val))


def float(val: 'Optional[b_float]' = None) -> PythonValue:
    """Returns a Float wrapped into a PythonValue"""
    # assert val is None or isinstance(val, __builtins__['float']), \
    #     f"I accept either a float or a None value, but I was given {type(val)}"
    return PythonValue(Float(val))


def bool(val: 'Optional[b_bool]' = None) -> PythonValue:
    """Returns a Bool wrapped into a PythonValue"""
    return PythonValue(Bool(val))


def __createNonePV() -> Any:
    """Building a single wrapped value for NoneType

    Why waste memory on a class that contains a unique element.

    Creating an element of type NoneType and returning it every single time.

    :return: a NoneType wrapped into a PythonValue
    """
    none = PythonValue(NoneType())

    def retNone() -> PythonValue:
        nonlocal none
        return none
    return retNone


none = __createNonePV()  # type: Callable[[], PythonValue]


def list(lst: 'Optional[List_[PythonValue]]' = None) -> PythonValue:
    """Returns a List wrapped into a PythonValue"""
    return PythonValue(List(lst=lst))


def tuple(*tpl: 'PythonValue') -> PythonValue:
    """Returns a Tuple wrapped into a PythonValue"""
    return PythonValue(Tuple(lst=tpl))  # type: ignore


Top = PythonValue.top()
ModuleTop = PythonValue(BuiltinModule.top())
