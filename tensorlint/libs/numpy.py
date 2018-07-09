import typing as ty
from tensorlint.internals import (
    Any, Value, Int, errors, TL_TypeError, addRules
)
from tensorlint.internals.tools import NonImplementedTL

__all__ = ['zeros', 'ones', 'dot', 'float32', 'float64']

T = ty.TypeVar('T')
Pos = ty.Tuple[int,int]

# TODO(helq): copy notation (names used) from the library

class array(Value):
    type_ = None # type: ty.Any
    shape = None # type: ty.Tuple[Int, ...]

    add_impls = [None, Int] # type: ty.List[ty.Optional[ty.Type]]
    impls_inherit = ['__radd__', '__rmul__']
    def __init__(self,
                 type_: ty.Type[T],
                 shape: 'ty.Tuple[Int,...]') -> None:
        self.type_ = type_
        self.shape = shape

    # Everything happens here, this is where the type checking is done
    def __binop(self, opname: str, other: Value, pos: ty.Optional[Pos] = None): # type: ignore
        if isinstance(other, Int):
            # TODO(helq): the type of the resulting tensor is not the original,
            # but it depends on the value of the variable
            if self.type_ == int:
                return array(self.type_, self.shape)
            else:
                return array(Any, self.shape)
        elif isinstance(other, array):
            if self.type_ != other.type_:
                new_type = Any
            else:
                new_type = self.type_

            # TODO(helq): add broadcasting rules
            if self.shape == other.shape:
                new_shape = self.shape
            else:
                # TODO(helq): Improve error, and send signal to stop computing everything
                global errors
                errors.append( TL_TypeError("The shapes can't be united, they are not the same", -1, -1) )
                raise NonImplementedTL("`tensor.__add__` hasn't been completely implemented yet")
            return array(new_type, new_shape)
        else:
            return NotImplemented

    def __add__(self, other: Value, pos: ty.Optional[Pos] = None) -> Value:
        return self.__binop('add', other, pos) # type: ignore

    def __mul__(self, other: Value, pos: ty.Optional[Pos] = None) -> Value:
        return self.__binop('mul', other, pos) # type: ignore

    # TODO(helq): make this abstract, each class should implement it or use
    # reflection to print the right name always
    def __repr__(self) -> str:
        return 'np.array('+repr(self.type_)+', '+repr(self.shape)+')'

class NdarrayDtype():
    pass

class float64(NdarrayDtype):
    pass

class float32(NdarrayDtype):
    pass

def zeros( val : ty.Tuple[Int, ...], dtype: ty.Type = float64 ) -> array:
    # TODO(helq): typecheck that the pass values are of the correct type and
    # that they are valid (no negative values)
    return array(dtype, val)

def ones( val : ty.Tuple[Int, ...], dtype: ty.Type = float64 ) -> array:
    return array(dtype, val)

def dot( vall: Value, valr: Value ) -> Value:
    if isinstance(vall, array) and isinstance(valr, array):
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
                        return array(vall.type_, (vall.shape[0], valr.shape[1]))

        print(vall.type_, valr.type_)
        raise NonImplementedTL("`numpy.dot` hasn't been implemented for tensors of different types yet :(")
    raise NonImplementedTL("`numpy.dot` fails if one of the parameters is not an array")
