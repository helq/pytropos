from typing import Tuple, Union
from typing import Optional, Dict  # noqa: F401

from ..values.python_values import PythonValue
from ..errors import TypeCheckLogger
from ..abstract_domain import AbstractDomain

# from .global_scope import FrozenGlobalScope, GlobalScope
# from .cell import Cell

from ..miscelaneous import Pos

__all__ = ['Store']


# TODO(helq): The global scope doesn't not contain builtins, but the builtins are always
# present and should be checked if the variable is not local/nonlocal or global

class Store(AbstractDomain):
    """
    A store saves the variables values.
    """

    def __init__(self, store: 'Union[Store, int]' = 0) -> None:
        """
        A store can be initialised.

        @param store: If it is 1, then the Store is top.
                      If it is 0, an empty store is created
        """
        if isinstance(store, int):
            if store == 1:
                self._im_top = True
            else:
                self._im_top = False
                self._global_scope = {}  # type: Dict[str, PythonValue]
        else:
            self._im_top = False
            self._global_scope = store._global_scope.copy()

    def copy(self) -> 'Store':
        """
        Returns a copy of the Store.
        Any modification to this shouldn't alter the original store.
        """
        new_store = Store(self)

        mut_heap = {}  # type: Dict[int, PythonValue]
        new_globals = new_store._global_scope

        for k, val in self._global_scope.items():
            if not val.is_mut():
                new_globals[k] = val  # non mutable objects don't need to be cloned
            else:
                new_globals[k] = val.copy_mut(mut_heap)

        return new_store

    def __getitem__(self, key_: Union[str, Tuple[str, Pos]]) -> PythonValue:
        if not isinstance(key_, tuple):
            key = key_
            src_pos = None  # type: Optional[Pos]
        else:
            key, src_pos = key_

        if key in self._global_scope:
            return self._global_scope[key]

        TypeCheckLogger().new_warning(
            "W201",
            "Global variable `{}` isn't set".format(key),
            src_pos
        )

        toret = self._global_scope[key] = PythonValue.top()
        return toret

    def __setitem__(self, key_: Union[str, Tuple[str, Pos]], value: PythonValue) -> None:
        if not isinstance(key_, tuple):
            key = key_
            src_pos = None  # type: Optional[Pos]
        else:
            key, src_pos = key_

        self._global_scope[key] = value

    def __delitem__(self, key_: Union[str, Tuple[str, Pos]]) -> None:
        if not isinstance(key_, tuple):
            key = key_
            src_pos = None  # type: Optional[Pos]
        else:
            key, src_pos = key_

        if key in self._global_scope:
            del self._global_scope[key]
        else:
            TypeCheckLogger().new_warning(
                "W201",
                "Global variable `{}` isn't set".format(key),
                src_pos
            )

    def __contains__(self, item: str) -> bool:
        return bool(item in self._global_scope)

    def __repr__(self) -> str:
        return f"Store({self._global_scope})"

    __top_value = None  # type: Store

    @classmethod
    def top(cls) -> 'Store':
        if not Store.__top_value:
            Store.__top_value = Store(1)
        return Store.__top_value

    def is_top(self) -> bool:
        return self._im_top

    def join(self, other: 'Store') -> 'Store':
        left_keys = set(self._global_scope)
        right_keys = set(other._global_scope)
        keys = left_keys.union(right_keys)
        new_store = Store()
        new_globals = new_store._global_scope
        mut_heap = {}  # type: Dict[Tuple[str, int], Tuple[int, int, PythonValue]]

        for key in keys:
            # The key is only in the left store
            if key not in right_keys:
                # handling the mutable case
                left_val = self._global_scope[key]
                if left_val.is_mut():
                    left_val.convert_into_top(mut_heap, "left")

                new_globals[key] = PythonValue.top()

            # The key is only in the right store
            elif key not in left_keys:
                # handling the mutable case
                right_val = self._global_scope[key]
                if right_val.is_mut():
                    right_val.convert_into_top(mut_heap, "right")

                new_globals[key] = PythonValue.top()

            # the key is in both stores
            else:
                val1 = self._global_scope[key]
                val2 = other._global_scope[key]

                if val1.is_mut():
                    if val2.is_mut():  # both (val1 and val2) are mutable
                        new_globals[key] = val1.join_mut(val2, mut_heap)

                    else:  # val1 mutable, val2 not mutable
                        val1.convert_into_top(mut_heap, 'left')
                        new_globals[key] = PythonValue.top()

                else:
                    if val2.is_mut():  # val1 not mutable, val2 mutable
                        val2.convert_into_top(mut_heap, 'right')
                        new_globals[key] = PythonValue.top()

                    else:  # both (val1 and val2) are not mutable
                        new_globals[key] = val1.join(val2)

        return new_store

    def widen_op(self, other: 'Store') -> 'Tuple[Store, bool]':
        """
        Works like `.join` but it is warrantied to terminate if it is applied over and
        over increasing values.
        """
        keys = set(self._global_scope).union(other._global_scope)
        common_keys = set(self._global_scope).intersection(other._global_scope)
        new_store = Store()
        fix_point = True

        for key in keys:
            if key not in common_keys:
                new_store._global_scope[key] = PythonValue.top()
                fix_point = False
            else:
                val1 = self._global_scope[key]
                val2 = other._global_scope[key]

                # if the same object is saved in both Stores, don't copy it!
                if val1 is val2:
                    new_store._global_scope[key] = val1
                else:
                    new_store._global_scope[key], fix = val1.widen_op(val2)
                    if not fix:
                        fix_point = False

        return new_store, fix_point
