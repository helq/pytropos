from abc import ABC, abstractmethod

from typing import Any
from typing import Tuple  # noqa: F401


class AbstractDomain(ABC):
    """
    Base class to define an Abstract Domain.
    An object from an Abstract Domain is an element from a lattice, therefore the abstract
    domain must define a Lattice structure with its order relation, and top and bottom
    values.
    Additional operations to the Lattice are:
    - Join
    - Merge
    - Widening Operator (optional)
    - Narrowing Operator (optional)
    """

    @classmethod
    @abstractmethod
    def top(cls) -> Any:
        """Returns the Top element from the lattice"""
        raise NotImplementedError()

    # @classmethod
    # @abstractmethod
    # def bottom(cls) -> Any:
    #     """Returns the Bottom element from the lattice"""
    #     raise NotImplementedError()

    @abstractmethod
    def is_top(self) -> bool:
        """Returns True if this object is the top of the lattice"""
        raise NotImplementedError()

    # @abstractmethod
    # def is_bottom(self) -> bool:
    #     """Returns True if this object is the bottom of the lattice"""
    #     raise NotImplementedError()

    # @abstractmethod
    # def smaller_than(self, other: Any) -> bool:
    #     """Returns True if this object is "smaller" than other in the lattice"""
    #     raise NotImplementedError()

    @abstractmethod
    def join(self, other: Any) -> Any:
        """Performs 'Least Upper Bound' operation between self and other"""
        raise NotImplementedError()

    # @abstractmethod
    # def merge(self, other: Any) -> Any:
    #     """Performs 'Greatest Lower Bound' operation between self and other"""
    #     raise NotImplementedError()

    def widen_op(self, other: Any) -> 'Tuple[Any, bool]':
        """Performs the Widen operation on self and other"""
        raise NotImplementedError()

    def narrow_op(self, other: Any) -> 'Tuple[Any, bool]':
        """Performs the Narrow operation on self and other"""
        raise NotImplementedError()

    def __bool__(self) -> bool:
        """This prevents to use any Abstract Domain as a boolean.

        I have made several times the same mistake. I've wrote something like::

            if val.top():
                ...

        when I meant::

            if val.is_top():
                ...
        """
        raise ValueError("Why am I being used as a bool!!")
