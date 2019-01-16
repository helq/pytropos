from typing import TYPE_CHECKING

from ..values.builtin_values import Bool
from ..values.python_values import PythonValue
from ..store import Store

if TYPE_CHECKING:
    from typing import Callable, Optional  # noqa: F401


__all__ = ['runIf', 'runWhile']


MAX_LOOPS = 100


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
        # print(f"store_if = {store_if}")
        if else_:
            store = else_(store)
            # print(f"store_else = {store}")
        # TODO(helq): replace join with join_destructive
        return store.join(store_if)
    elif bool_qst.val is True:
        return if_(store)
    else:
        return else_(store) if else_ else store


def runWhile(
        store: Store,
        while_qst: 'Callable[[Store], PythonValue]',
        while_: 'Callable[[Store], Store]'
) -> 'Store':
    """
    Runs the code ten times, if the condition doesn't become False, then tries to find a
    fix point using `widen_op`.
    """

    for i in range(MAX_LOOPS):
        val = while_qst(store).bool()
        assert isinstance(val.val, Bool)
        bool_val = val.val

        if bool_val.is_top():  # Bool(?)
            break
        elif bool_val.val is False:
            return store
        # else bool_val is True the execution of while_ should continue

        store = while_(store)

    # If I arrived here, I know that 10 loops wheren't enough or bool_var is Bool(?),
    # either way we need to find a fix point
    fix_point = False
    while not fix_point:
        new_store = while_(store.copy())  # TODO(helq): change for .copy_soft
        while_qst(store)
        store, fix_point = store.widen_op(new_store)  # TODO(helq): change for widen_op_destructive

    # TODO(helq): after the widen_op is applied, use narrow_op!
    # while not fix_point:
    #     new_store = while_(store.copy())
    #     while_qst(store)
    #     store, fix_point = store.narrow_op(new_store)

    return store
