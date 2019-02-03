from typing import Optional, Dict, Any

from ..values import Top
from ..store import Store
from ..errors import TypeCheckLogger
from ..values.abstract_value import AbstractValue
from ..values.python_values.python_values import \
    Args, PythonValue, AttrsContainer, AttrsTopContainer
from ..values.python_values.wrappers import BuiltinType
from ..values.builtin_values import Int

from ..miscelaneous import Pos

__all__ = ["print", "show_store", "int"]


class ShowStore:
    def call(
            self,
            store: Store,
            args: Args,
            pos: Optional[Pos] = None
    ) -> None:
        if args.vals:
            val = args.vals[0]
            if isinstance(val.val, AbstractValue):
                msg = f"The value of the expresion is: {val}" \
                    f" and its of type '{val.val.type_name}'"
            else:
                msg = f"The value of the expresion is: {val}"

            TypeCheckLogger().new_warning("F002", msg, pos)
        else:
            TypeCheckLogger().new_warning("F002", f"Store: {store}", pos)


# TODO(helq): print should return None
# TODO(helq): check for input values
print = Top

# Abusing of python duck typing, this function can be called but it will make everything
# fail if anything else is done with this value
# TODO(helq): ShowStore should be wrapped by a PythonValue and an AbstractValue
show_store = ShowStore()


class function_type_int(BuiltinType):
    """Similar to None, there is only one instance of it!!"""
    def __init__(  # noqa: C901
            self,
            children: 'Optional[Dict[Any, PythonValue]]' = None
    ) -> None:
        super().__init__(children=children)

        if children is None:
            return

    @property
    def abstract_repr(self) -> str:
        return "<class 'int'>"

    @property
    def type_name(self) -> str:
        return 'type[int]'

    __top = None  # type: function_type_int

    @classmethod
    def top(cls) -> 'function_type_int':
        if cls.__top is None:
            cls.__top = cls()
        return cls.__top

    def is_top(self) -> 'bool':
        return True

    def get_absvalue(self) -> 'PythonValue':
        return PythonValue(Int.top())

    def get_attrs(self) -> 'AttrsContainer':
        # TODO(helq): show error message, similar to how list does it
        return AttrsTopContainer()


int = PythonValue(function_type_int())
