import typing as ty
# from typing import Optional

# from tensorlint.internals.tools import Pos

from .value import Value

__all__ = ['Function']


class Function(Value):
    pass


class MockFunction(Function):
    def __init__(self, fun: ty.Callable) -> None:
        self.fun = fun

    def call(self, *args: ty.Any, **kargs: ty.Any) -> ty.Any:
        return self.fun(*args, **kargs)
