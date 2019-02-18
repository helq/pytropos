from typing import Optional, Any, TYPE_CHECKING

from ..values import Top
from ..store import Store
from ..errors import TypeCheckLogger
from ..values.abstract_value import AbstractValue
from ..values.python_values.python_values import Args, PythonValue, AttrsTopContainer
from ..values.python_values.wrappers import BuiltinType
from ..values.builtin_values import Int, Bool, Float

from ..miscelaneous import Pos

if TYPE_CHECKING:
    from typing import Dict  # noqa: F401
    from .python_values import AttrsContainer  # noqa: F401

__all__ = ["print", "show_store", "int", "input"]


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
input = Top

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

    def fun_call(self, store: Any, args: 'Args', pos: Optional[Pos]) -> PythonValue:
        top = PythonValue(Int.top())
        int = __builtins__['int']  # type: ignore

        if args.args is not None:
            TypeCheckLogger().new_warning(
                "F001",
                f"Sorry! Pytropos doesn't support calling 'int' with a starred variable",
                pos)
            return top

        if args.kargs and (len(args.kargs) > 1 or (set(args.kargs) - {'base'})):
            TypeCheckLogger().new_warning(
                "E014",
                f"TypeError: {self.type_name}() takes only one keyword: 'base'",
                pos)
            return top

        total_args = len(args.vals) + (len(args.kargs) if args.kargs else 0)

        if total_args > 2:
            TypeCheckLogger().new_warning(
                "E014",
                f"TypeError: {self.type_name}() takes at most 2 arguments "
                f"{len(args.vals)} given",
                pos)
            return top

        if total_args == 2:
            TypeCheckLogger().new_warning(
                "F001",
                f"Sorry! Pytropos doesn't support 'base' keyword for 'int'",
                pos)
            return top

        if len(args.vals) == 0:
            return PythonValue(Int(0))

        n = args.vals[0]
        if n.is_top():
            return top

        if isinstance(n.val, (Int, Float, Bool)) and not n.val.is_top():
            assert n.val.val is not None
            return PythonValue(Int(int(n.val.val)))

        return top


int = PythonValue(function_type_int())
