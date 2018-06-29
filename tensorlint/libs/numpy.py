from typing import Tuple
from tensorlint.internals import Value, Tensor, Tensor, NonImplementedTL

__all__ = ['zeros', 'ones', 'dot']

# TODO(helq): copy notation (names used) from the library

def zeros( val : Tuple[Value, ...] ) -> Tensor:
    raise NonImplementedTL("`numpy.zeros` hasn't been implemented yet :(")

def ones( val : Tuple[Value, ...] ) -> Tensor:
    raise NonImplementedTL("`numpy.ones` hasn't been implemented yet :(")

def dot( vall: Tensor, valr: Tensor ) -> Tensor:
    raise NonImplementedTL("`numpy.dot` hasn't been implemented yet :(")
