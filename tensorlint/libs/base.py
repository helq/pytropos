from tensorlint.internals import Value, Int, Iterable
from tensorlint.internals.tools import NonImplementedTL

__all__ = ['range', 'print']

def range( val : Int ) -> Iterable:
    # TODO(helq): optionally, in the future we could check for the type of the
    # value passed, it should be an int
    return Iterable(Int())

def print( *val : Value ) -> None:
    pass
