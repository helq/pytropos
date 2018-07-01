import typing as ty
from tensorlint.internals import (
    Value, Int, errors, TL_TypeError
)
from tensorlint.internals.numpy import NumpyTensor
from tensorlint.internals.tools import NonImplementedTL

__all__ = ['zeros', 'ones', 'dot', 'float32', 'float64']

T = ty.TypeVar('T')

# TODO(helq): copy notation (names used) from the library

class NdarrayDtype():
    pass

class float64(NdarrayDtype):
    pass

class float32(NdarrayDtype):
    pass

def zeros( val : ty.Tuple[Int, ...], dtype: ty.Type = float64 ) -> NumpyTensor:
    # TODO(helq): typecheck that the pass values are of the correct type and
    # that they are valid (no negative values)
    return NumpyTensor(dtype, val)

def ones( val : ty.Tuple[Int, ...], dtype: ty.Type = float64 ) -> NumpyTensor:
    return NumpyTensor(dtype, val)

def dot( vall: NumpyTensor, valr: NumpyTensor ) -> NumpyTensor:
    if vall.type_ == valr.type_:
        if len(vall.shape) != 2 or len(valr.shape) != 2:
            errors.append( TL_TypeError("Some tensor doesn't have dimension 2", -1, -1) )
            raise NonImplementedTL("`numpy.dot` matrix multiplication requires tensors of dimension 2")
        # TODO(helq): define __eq__ to check for equality of 'Value's
        else:
            sleft  = vall.shape[1].n
            sright = valr.shape[0].n
            if (sleft is not None and sright is not None):
                if sleft != sright:
                    errors.append( TL_TypeError("Matrices are not compatible for multiplication", -1, -1) )
                    # TODO(helq): create warnings in case an operation potentially
                    # fails but we're not sure, like when adding two numbers and one of
                    # them is a symbol
                    raise NonImplementedTL("`numpy.dot` Matrices are not compatible for multiplication")
                else:
                    return NumpyTensor(vall.type_, (vall.shape[0], valr.shape[1]))

    raise NonImplementedTL("`numpy.dot` hasn't been implemented for tensors of different types yet :(")
