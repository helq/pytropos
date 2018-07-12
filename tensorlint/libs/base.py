from tensorlint.internals import Value, Int, Iterable
from tensorlint.internals.tools import NonImplementedTL

from typing import Optional, Tuple

__all__ = ['range', 'print']

Pos = Tuple[int,int]

def range(val: Int,
          val2: Optional[Int] = None,
          sep: Optional[Int] = None,
          src_pos: Optional[Pos] = None) -> Iterable:
    # TODO(helq): optionally, in the future we could check for the type of the
    # value passed, it should be an int
    return Iterable(Int())

def print( *args: Value, **kargs: Value ) -> None:
    pass
