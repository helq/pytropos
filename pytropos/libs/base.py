from pytropos.internals import Int, Iterable, Any
from pytropos.internals.tools import Pos

from pytropos.internals.values.function import MockFunction

from typing import Optional

__all__ = ['range', 'print']


@MockFunction
def range(val: Int,
          val2: Optional[Int] = None,
          sep: Optional[Int] = None,
          src_pos: Optional[Pos] = None) -> Iterable:
    # TODO(helq): optionally, in the future we could check for the type of the
    # value passed, it should be an int
    return Iterable(Int())


print = Any()
