import typing as ty
from tensorlint.internals.values import (
    Value, Int
)
from tensorlint.internals.tools import NonImplementedTL
from tensorlint.internals.errors import errors, TL_TypeError

__all__ = ["NumpyTensor"]

T = ty.TypeVar('T')

# class NumpyTensor(Value[T], metaclass=ABCMeta):
class NumpyTensor(Value[T]):
    type_ = None # type: ty.Type[T]
    shape = None # type: ty.Tuple[Int, ...]
    def __init__(self,
                 type_ : ty.Type[T],
                 shape : 'ty.Tuple[Int,...]') -> None:
        self.type_ = type_
        self.shape = shape

    # Everything happens here, this is where the type checking is done
    def __add__(self, other : 'ty.Union[Int, NumpyTensor]') -> 'NumpyTensor':
        if isinstance(other, Int):
            # TODO(helq): the type of the resulting tensor is not the original,
            # but it depends on the value of the variable
            if self.type_ == int:
                return NumpyTensor(self.type_, self.shape)
            else:
                return NumpyTensor(type(ty.Any), self.shape)
        else:
            if self.type_ == other.type_:
                new_type = type(ty.Any)
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
            return NumpyTensor(self.type_, new_shape)

    def __radd__(self, other : 'ty.Union[Int, NumpyTensor]') -> 'NumpyTensor':
        return self.__add__(other)

    # TODO(helq): make this abstract, each class should implement it or use
    # reflection to print the right name always
    def __repr__(self) -> str:
        return 'tl.NumpyTensor('+repr(self.type_)+', '+repr(self.shape)+')'

