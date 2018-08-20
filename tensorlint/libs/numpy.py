import typing as ty
from tensorlint.internals import (
    Any, Value, Int, binop_rules
)
from tensorlint.internals.errors import TypeCheckLogger
from tensorlint.internals.tools import NonImplementedTL, Pos

__all__ = ['zeros', 'ones', 'dot', 'float32', 'float64']

T = ty.TypeVar('T')


# TODO(helq): copy notation (names used) from the library


@binop_rules.extractRulesFromClass
class ndarray(Value):
    type_ = None  # type: ty.Any
    shape = None  # type: ty.Tuple[Int, ...]

    add_impls = [None, Int]  # type: ty.List[ty.Optional[ty.Type]]
    impls_inherit = ['__radd__', '__rmul__']

    def __init__(self,
                 type_: ty.Type[T],
                 shape: 'ty.Tuple[Int,...]') -> None:
        self.type_ = type_
        self.shape = shape

    # Everything happens here, this is where the type checking is done
    def __binop(self, opname: str, other: Value, src_pos: ty.Optional[Pos] = None):  # type: ignore
        if isinstance(other, Int):
            # TODO(helq): the type of the resulting tensor is not the original,
            # but it depends on the value of the variable
            if self.type_ == int:
                return ndarray(self.type_, self.shape)
            else:
                return ndarray(Any, self.shape)
        elif isinstance(other, ndarray):
            if self.type_ != other.type_:
                new_type = Any
            else:
                new_type = self.type_

            # TODO(helq): add broadcasting rules
            if self.shape == other.shape:
                new_shape = self.shape
            else:
                # TODO(helq): Improve error, and send signal to stop computing everything
                TypeCheckLogger().new_warning(
                    "NOIDEA",
                    "The shapes can't be united, they are not the same",
                    (-1, -1))
                raise NonImplementedTL("`tensor.__add__` hasn't been completely implemented yet")
            return ndarray(new_type, new_shape)
        else:
            return NotImplemented

    def add_op(self, other: Value, src_pos: ty.Optional[Pos] = None) -> Value:  # type: ignore
        return self.__binop('add', other, src_pos)  # type: ignore

    def mul_op(self, other: Value, src_pos: ty.Optional[Pos] = None) -> Value:  # type: ignore
        return self.__binop('mul', other, src_pos)  # type: ignore

    # TODO(helq): make this abstract, each class should implement it or use
    # reflection to print the right name always
    def __repr__(self) -> str:
        return 'np.ndarray('+repr(self.type_)+', '+repr(self.shape)+')'


class NdarrayDtype():
    pass


class float64(NdarrayDtype):
    pass


class float32(NdarrayDtype):
    pass


def zeros(val: ty.Tuple[Int, ...],
          dtype: ty.Type = float64,
          src_pos: ty.Optional[Pos] = None) -> ndarray:
    # TODO(helq): typecheck that the pass values are of the correct type and
    # that they are valid (no negative values)
    return ndarray(dtype, val)


# TODO(helq): check that the values passed are ints, and not other thing
# (except for Any), in that case use congruent to check for the validity of the
# values
def ones(val: ty.Tuple[Int, ...],
         dtype: ty.Type = float64,
         src_pos: ty.Optional[Pos] = None) -> ndarray:
    return ndarray(dtype, val)


def dot(vall: Value,
        valr: Value,
        src_pos: ty.Optional[Pos] = None) -> Value:
    if isinstance(vall, ndarray) and isinstance(valr, ndarray):
        if vall.type_ == valr.type_:
            if len(vall.shape) != 2 or len(valr.shape) != 2:
                line, col = (-1, -1) if src_pos is None else src_pos
                # TODO(helq): add values of the shapes of the tensors
                TypeCheckLogger().new_warning(
                    "NOIDEA",
                    "Some tensor doesn't have dimension 2",
                    (line, col))
                raise NonImplementedTL(
                    "`numpy.dot` matrix multiplication requires tensors of dimension 2")
            # TODO(helq): define __eq__ to check for equality of 'Value's
            else:
                sleft  = vall.shape[1].n
                sright = valr.shape[0].n
                if (sleft is not None and sright is not None):
                    if sleft != sright:
                        line, col = (-1, -1) if src_pos is None else src_pos
                        TypeCheckLogger().new_warning(
                            "NOIDEA",
                            "Matrices are not compatible for multiplication",
                            (line, col))
                        # TODO(helq): create warnings in case an operation potentially
                        # fails but we're not sure, like when adding two numbers and one of
                        # them is a symbol
                        raise NonImplementedTL(
                            "`numpy.dot` check for matrix compatibility not completely coded")
                    else:
                        return ndarray(vall.type_, (vall.shape[0], valr.shape[1]))

        print(vall.type_, valr.type_)
        raise NonImplementedTL(
            "`numpy.dot` hasn't been implemented for tensors of different types yet :(")
    raise NonImplementedTL("`numpy.dot` fails if one of the parameters is not an ndarray")
