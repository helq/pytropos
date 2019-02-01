from typing import Optional

from ..values import Top
from ..store import Store
from ..errors import TypeCheckLogger
from ..values.abstract_value import AbstractValue
from ..values.python_values.python_values import Args

from ..miscelaneous import Pos

__all__ = ["print", "show_store"]


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
