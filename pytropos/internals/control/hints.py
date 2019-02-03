from typing import Optional

from ..values.python_values import PythonValue
from ..values.python_values.wrappers import BuiltinClass, BuiltinType
from ..errors import TypeCheckLogger
from ..miscelaneous import Pos

__all__ = ['annotation']


def annotation(ann: PythonValue, expr: PythonValue, pos: 'Optional[Pos]') -> PythonValue:
    """Checks if the annotation for the expression improves "accuracy" on the value of the
    variable."""
    typeann = ann.val
    if isinstance(typeann, BuiltinType):
        type_ = typeann.get_absvalue()
    elif isinstance(typeann, BuiltinClass):
        type_ = typeann.class_top()
    else:
        return expr

    if type_ == expr:
        return expr
    elif type_ < expr:
        return type_

    TypeCheckLogger().new_warning(
        "W301",
        f"not ({type_} < {expr}). Incompatible types in assignment "
        f"(expression has type {expr}, variable has type {type_})",
        pos)

    return expr