from typing import Iterable, Union
from tensorlint.internals import Value, Tensor, NonImplementedTL

__all__ = ['range', 'print']

def range( val : Value ) -> Value:
    raise NonImplementedTL("`range` hasn't been implemented yet :(")

def print( *val : Union[Value, Tensor] ) -> None:
    pass
