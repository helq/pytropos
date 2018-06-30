from typing import Tuple, TypeVar
from tensorlint.internals import (
    Value, Tensor, Tensor, NonImplementedTL, errors, TL_TypeError
)

__all__ = ['zeros', 'ones', 'dot']

T = TypeVar('T')

# TODO(helq): copy notation (names used) from the library

class NumpyTensor(Tensor[T]):
    def __repr__(self) -> str:
        return 'np.NumpyTensor('+repr(self.type_)+', '+repr(self.shape)+')'

class NdarrayDtype():
    pass

class float64(NdarrayDtype):
    pass

class float32(NdarrayDtype):
    pass

def zeros( val : Tuple[Value, ...] ) -> NumpyTensor:
    # TODO(helq): typecheck that the pass values are of the correct type and
    # that they are valid (no negative values)
    return NumpyTensor(float64, val)

def ones( val : Tuple[Value, ...] ) -> NumpyTensor:
    return NumpyTensor(float64, val)

def dot( vall: NumpyTensor, valr: NumpyTensor ) -> NumpyTensor:
    if vall.type_ == valr.type_:
        if len(vall.shape) != 2 or len(valr.shape) != 2:
            errors.append( TL_TypeError("Some tensor doesn't have dimension 2", -1, -1) )
            raise NonImplementedTL("`numpy.dot` matrix multiplication requires tensors of dimension 2")
        # TODO(helq): define __eq__ to check for equality of 'Value's
        elif vall.shape[1].val != valr.shape[0].val:
            errors.append( TL_TypeError("Matrices are not compatible for multiplication", -1, -1) )
            # TODO(helq): create warnings in case an operation potentially
            # fails but we're not sure, like when adding two numbers and one of
            # them is a symbol
            raise NonImplementedTL("`numpy.dot` matrix multiplication doesn't check for cases where a variable has an Undefined value")
        else:
            return NumpyTensor(vall.type_, (vall.shape[0], valr.shape[1]))

    raise NonImplementedTL("`numpy.dot` hasn't been implemented for tensors of different types yet :(")
