import typing as ty
from typing import Optional, Tuple

from pytropos.internals.tools import Pos

from .value import Value

__all__ = ['Function']


class Function(Value):
    pass


class MockFunction(Function):
    def __init__(self, fun: ty.Callable) -> None:
        self.fun = fun

    def call(self,
             args: Tuple['Value'],
             vault: ty.Any,
             src_pos: Optional[Pos] = None
             ) -> Value:
        return self.fun(*args, src_pos=src_pos)  # type: ignore
