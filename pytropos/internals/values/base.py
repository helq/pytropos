from abc import ABC, abstractmethod

import typing as ty
from typing import Tuple, Optional

from ..tools import Pos

__all__ = ['AbstractValue', 'Any']


# TODO(helq): add `get` method to simulate access to member values like, num.some.var
class AbstractValue(ABC):
    """
    All variables in pytropos must derivate from `AbstractValue`. `AbstractValue` is just
    like `object` for all objects in python.
    """

    @abstractmethod
    def join(self, other: ty.Any) -> ty.Any:
        """Returns the new value that captures the other two (self and other)"""
        raise NotImplementedError()

    # TODO(helq): This should be removed!
    @abstractmethod
    def congruent_inside(self, other: ty.Any) -> bool:
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
                 args: Tuple[ty.Any],
                 vau: ty.Any,
                 src_pos: Optional[Pos]
                 ) -> ty.Any:
        """The Abstract Value is invoked as a function"""
        raise NotImplementedError()

    def call_getitem(self, key: ty.Any) -> ty.Any:
        """Invoking Abstract Value's __getitem__"""
        raise NotImplementedError()

    def call_setitem(self, key: ty.Any, val: ty.Any) -> ty.Any:
        """Invoking Abstract Value's __getitem__"""
        raise NotImplementedError()

    def op_add(self, other: ty.Any) -> ty.Any:
        """
        This operation defines how to add two values of the same type.

        To define how to add to another value use op_add_TYPE (where TYPE is the type of
        the value, e.g., op_add_Int)
        """
        raise NotImplementedError()


# TODO(helq): Implement all methods special method names
# https://docs.python.org/3/reference/datamodel.html#special-method-names
class Any(AbstractValue):
    error_when_used = False

    def join(self, other: ty.Any) -> ty.Any:
        raise NotImplementedError()

    def congruent_inside(self, other: ty.Any) -> bool:
        raise NotImplementedError()

    @property
    def type_name(self) -> str:
        raise NotImplementedError()

    @property
    def abstract_repr(self) -> str:
        return "any?"

    def checkErrorIfUsed(self) -> None:
        if Any.error_when_used:
            raise Exception("Trying to use Any value")

    def __init__(self, *args: ty.Any, **kargs: ty.Any) -> None:
        if len(args) > 0:
            if Any.error_when_used:
                raise Exception("Trying to construct Any value (with parms: {})".format(repr(args)))
        if Any.error_when_used:
            raise Exception("Trying to construct Any value")

    def __repr__(self) -> str:
        return "Any()"

    def __call__(self, *args, **kargs) -> 'Any':  # type: ignore
        return Any()
        # raise NotImplementedError()

    def __getattr__(self, name: str) -> 'Any':
        return Any()

    def __getitem__(self, key: ty.Any) -> 'Any':
        return Any()

    def __setitem__(self, key: ty.Any, val: ty.Any) -> None:
        pass

    def __delitem__(self, key: ty.Any) -> None:
        pass
