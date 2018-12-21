import typing as ty
from typing import Optional, Type

from pytropos.internals.values.base import AbstractValue
from pytropos.internals import Any, Int
from pytropos.internals.operations.base import add_ops_to_global
from pytropos.internals.errors import TypeCheckLogger
from pytropos.internals.tools import NonImplementedPT, Pos
from pytropos.internals.rules import congruent

from pytropos.internals.values.function import MockFunction

__all__ = ['zeros', 'ones', 'dot', 'float32', 'float64']

T = ty.TypeVar('T')


# TODO(helq): copy notation (names used) from the library


@add_ops_to_global
class ndarray(AbstractValue):
    def __init__(self,
                 shape: 'Optional[ty.Tuple[AbstractValue,...]]',
                 type: Optional[Type]) -> None:
        self.type = type
        self.shape = shape

    def join(self, other: 'AbstractValue') -> 'AbstractValue':
        raise NotImplementedError()

    def congruent_inside(self, other: 'AbstractValue') -> bool:
        raise NotImplementedError()

    @property
    def type_name(self) -> str:
        return "ndarray"

    @property
    def abstract_repr(self) -> str:
        raise NotImplementedError()

    # Everything happens here, this is where the type checking is done
    def __binop(self,  # type: ignore
                opname: str,
                other: AbstractValue,
                src_pos: ty.Optional[Pos] = None
                ):
        if isinstance(other, Int):
            # TODO(helq): the type of the resulting tensor is not the original,
            # but it depends on the value of the variable
            if self.type == int:
                return ndarray(self.shape, self.type)
            else:
                return ndarray(self.shape, Any)
        elif isinstance(other, ndarray):
            if self.type != other.type:
                new_type = Any  # type: Optional[Type]
            else:
                new_type = self.type

            # TODO(helq): add broadcasting rules
            if self.shape == other.shape:
                new_shape = self.shape
            else:
                # TODO(helq): Improve error, and send signal to stop computing everything
                TypeCheckLogger().new_warning(
                    "NOIDEA",
                    "The shapes can't be united, they are not the same",
                    src_pos)
                raise NonImplementedPT("`tensor.__add__` hasn't been completely implemented yet")
            return ndarray(new_shape, new_type)
        else:
            return NotImplemented

    def add_op(self,
               other: AbstractValue,
               src_pos: ty.Optional[Pos] = None
               ) -> AbstractValue:
        return self.__binop('add', other, src_pos)  # type: ignore

    def mul_op(self,
               other: AbstractValue,
               src_pos: ty.Optional[Pos] = None
               ) -> AbstractValue:
        return self.__binop('mul', other, src_pos)  # type: ignore

    # TODO(helq): make this abstract, each class should implement it or use
    # reflection to print the right name always
    def __repr__(self) -> str:
        return 'np.ndarray('+repr(self.type)+', '+repr(self.shape)+')'


class NdarrayDtype():
    pass


class float64(NdarrayDtype):
    pass


class float32(NdarrayDtype):
    pass


@MockFunction
def zeros(shape: ty.Tuple[Int, ...],
          dtype: Type = float64,
          src_pos: ty.Optional[Pos] = None) -> ndarray:
    new_shape = []  # type: ty.List[AbstractValue]
    for n, dim in enumerate(shape):
        if isinstance(dim, Any):
            new_shape.append(dim)
            continue
        if isinstance(dim, Int):
            if dim.n is not None and dim.n < 0:
                TypeCheckLogger().new_warning(
                    "E502",
                    "negative dimensions are not allowed",
                    src_pos)
                new_shape.append(Int())
            else:
                new_shape.append(dim)
        else:
            TypeCheckLogger().new_warning(
                "E502",
                "Dimension {} is not an integer! ".format(n+1) +
                "`{}` object cannot be interpreted as integer".format(dim.type_name),
                src_pos)
            new_shape.append(Any())
    return ndarray(tuple(new_shape), dtype)


ones = zeros


@MockFunction
def dot(vall: AbstractValue,
        valr: AbstractValue,
        src_pos: ty.Optional[Pos] = None) -> AbstractValue:
    if isinstance(vall, ndarray) and isinstance(valr, ndarray):
        if vall.type == valr.type:
            if vall.shape is None or len(vall.shape) != 2:
                TypeCheckLogger().new_warning(
                    "E503",
                    "`dot` Left tensor doesn't have dimension 2",
                    src_pos)
                # TODO: dectect possible new type
                return ndarray(None, None)
            if valr.shape is None or len(valr.shape) != 2:
                TypeCheckLogger().new_warning(
                    "E503",
                    "`dot` Right tensor doesn't have dimension 2",
                    src_pos)
                # TODO: dectect possible new type
                return ndarray(None, None)
            # TODO(helq): define __eq__ to check for equality of 'AbstractValue's
            else:
                sleft  = vall.shape[1]
                sright = valr.shape[0]
                if congruent(sleft, sright):
                    return ndarray((vall.shape[0], valr.shape[1]), vall.type)
                else:
                    left_n, right_n = sleft.abstract_repr, sright.abstract_repr
                    TypeCheckLogger().new_warning(
                        "E504",
                        "{} != {}. "
                        "Matrices are not compatible for multiplication. "
                        "The second dimension of the first array `{}` isn't equal to "
                        "the first dimension of the second array `{}`"
                        .format(left_n, right_n, left_n, right_n),
                        src_pos)
                    return ndarray(None, None)
        else:
            raise NonImplementedPT(
                "`numpy.dot` hasn't been implemented for tensors of different types yet :(")
    else:
        TypeCheckLogger().new_warning(
            "E505",
            "Both values in a `dot` operation must be ndarrays. " +
            ("Left" if isinstance(valr, ndarray) else "Right") +
            " value in dot operation is not an ndarray",
            src_pos)
        return Any()
