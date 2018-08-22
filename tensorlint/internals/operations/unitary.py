from typing import Optional, TYPE_CHECKING

from .base import uniop_rules
from ..values.value import Any, Value
from ..values.builtin_values import Bool, Int
from ..tools import Pos


__all__ = ['bool']

if TYPE_CHECKING:
    old_bool = __builtins__.bool
else:
    old_bool = bool


# ## Unary Operations ##

def bool(val: Value, src_pos: Optional[Pos] = None) -> Value:
    if isinstance(val, Any):
        return Any()
    res = uniop_rules.run('__bool__', val, src_pos)
    if res is NotImplemented:
        res = uniop_rules.run('__len__', val, src_pos)
        if isinstance(res, Int):
            return Bool() if res.n is None else Bool(old_bool(res.n))
    if res is NotImplemented:
        return Bool(False)
    elif isinstance(res, Bool):
        return res
    else:
        return Any()
