import typing as ty
from typing import Optional, Tuple

from pytropos.internals.tools import Pos

from .base import AbstractValue

__all__ = ['Function']


class Function(AbstractValue):
    pass


class MockFunction(Function):
    def __init__(self, fun: ty.Callable) -> None:
        self.fun = fun

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

    def call(self,
             args: Tuple['AbstractValue'],
             vault: ty.Any,
             src_pos: Optional[Pos] = None
             ) -> AbstractValue:
        return self.fun(*args, src_pos=src_pos)  # type: ignore

    @property
    def get(self) -> ty.Any:
        raise NotImplementedError()
