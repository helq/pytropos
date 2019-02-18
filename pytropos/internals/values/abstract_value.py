from abc import abstractmethod
from typing import Any, Optional
from typing import Tuple, Dict  # noqa: F401

from ..abstract_domain import AbstractDomain

from ..miscelaneous import Pos

__all__ = ['AbstractValue']


class AbstractValue(AbstractDomain):
    """
    All variables in pytropos must derivate from `AbstractValue`. `AbstractValue` is just
    like `object` for all objects in python.
    """

    @abstractmethod
    def join(self, other: Any) -> Any:
        """Returns the new value that captures the other two (self and other)"""
        raise NotImplementedError()

    def widen_op(self, other: Any) -> 'Tuple[Any, bool]':
        """Implement this method if the AbstractValue requires a widening operator"""
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
                 store: Any,
                 args: Any,
                 src_pos: Optional[Pos]
                 ) -> Any:
        """The Abstract Value is invoked as a function"""
        raise NotImplementedError()

    def get_attrs(self) -> Any:
        """Returns a dictionary like structure that contains all attributes the implements.

        It should return an object alike to Dict[str, PythonValue]"""
        raise NotImplementedError()

    def get_subscripts(self, pos: 'Optional[Pos]') -> Any:
        """Returns a dictionary like structure to access to the elements of an object with
        subscripts.

        It should return an object alike to Dict[PythonValue, PythonValue]"""
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

    # op_eq = op_OP
    # op_ne = op_OP
    op_lt = op_OP
    op_le = op_OP
    op_gt = op_OP
    op_ge = op_OP

    def op_bool(self, pos: Optional[Pos]) -> Any:
        """
        This operation must always return the AbstractValue Bool!

        Note: the type of this method does not say Bool but Any. A small inconvinience of
        how the modules are structured.
        """
        raise NotImplementedError()

    @abstractmethod
    def __eq__(self, other: Any) -> bool:
        """
        Determining if two Abstract Values are the same:
        Top == Top
        Top != Int(3)
        Int(5) == Int(5)
        """
        raise NotImplementedError()
