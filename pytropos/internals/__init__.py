from .values import (
    int, float, bool, none, list, tuple, Args, ModuleTop, Top
)
from .store import Store
from .control import runIf, runWhile, annotation

__all__ = [
    'int', 'float', 'bool', 'none', 'list', 'tuple', 'Args', 'ModuleTop', 'Top',
    'Store',
    'runIf', 'runWhile', 'annotation',
    'loadBuiltinFuncs'
]


def loadBuiltinFuncs(store: Store) -> None:
    from .builtin_funcs import functions as funcs
    for k in funcs.__all__:
        store._builtin_values[k] = getattr(funcs, k)
