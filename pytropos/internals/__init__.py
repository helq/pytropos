from .values import (  # noqa: F401
    int, float, bool, none, list, tuple, Args, ModuleTop
)
from .store import Store
from .control import runIf, runWhile

__all__ = [
    'int', 'float', 'bool', 'none', 'list', 'tuple', 'Args', 'ModuleTop',
    'Store',
    'runIf', 'runWhile',
    'loadBuiltinFuncs'
]


def loadBuiltinFuncs(store: Store) -> None:
    from .builtin_funcs import functions as funcs
    for k in funcs.__all__:
        store._builtin_values[k] = getattr(funcs, k)
