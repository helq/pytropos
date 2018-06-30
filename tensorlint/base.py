from typing import Iterable, Union, Type, Any
from tensorlint.internals import Value, Tensor, NonImplementedTL

__all__ = ['range', 'print']

def range( val : Value ) -> Value:
    # TODO(helq): optionally, in the future we could check for the type of the
    # value passed, it should be an int
    return Value(Type[Iterable[int]])

def print( *val : Union[Value, Tensor] ) -> None:
    pass
