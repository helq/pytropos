from typing import TYPE_CHECKING

from ..values.builtin_values import Bool
from ..values.python_values import PythonValue
from ..store import Store

if TYPE_CHECKING:
    from typing import Callable, Optional  # noqa: F401


__all__ = ['runIf']


def runIf(
        store: Store,
        if_qst: PythonValue,
        if_: 'Callable[[Store], Store]',
        else_: 'Optional[Callable[[Store], Store]]' = None,
) -> Store:
    """
    Runs an if branch. If the value of the question is unknown, it will run both
    branches and merge them.
    """
    bool_qst = if_qst.bool().val
    assert isinstance(bool_qst, Bool)

    if bool_qst.is_top():
        store_if = if_(store.copy())
        if else_:
            store = else_(store)
        # TODO(helq): replace join with join_destructive
        return store.join(store_if)
    elif bool_qst.val is True:
        return if_(store)
    else:
        return else_(store) if else_ else store
