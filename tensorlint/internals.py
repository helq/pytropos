from typing import (
    Any, Type, Optional, TypeVar, Generic, List, Tuple, Union, Iterable
)

__all__ = ['TL_TypeError', 'errors', 'warnings', 'Value', 'Tensor', 'for_loop']

T = TypeVar('T')

class NonImplementedTL(Exception):
    pass

class ValueAsWithStmt(Generic[T]):
    value = None  # type: Value[T]
    def __init__(self, val: 'Value[T]') -> None:
        self.value = val
    def __enter__(self):
        # type: (...) -> Value[T]
        return self.value
    def __exit__(self, exc_type, exc_value, traceback # type: ignore
                 ) -> None:
        pass

class TL_TypeError(object):
    msg        = None  # type: str
    lineno     = None  # type: int
    col_offset = None  # type: int
    def __init__(self, msg: str, lineno: int, col_offset: int) -> None:
        self.msg        = msg
        self.lineno     = lineno
        self.col_offset = col_offset

errors : List[TL_TypeError] = []
warnings : List[TL_TypeError] = []

class Value(Generic[T]):
    type_ = None # type: Type[T]
    # TODO(helq): change this type to something more complete, like
    # Union[T, Undefined, Symbol]
    val   = None # type: Optional[T]
    def __init__(self,
                 type_ : Type[T],
                 val   : Optional[T] = None) -> None:
        self.type_ = type_
        self.val   = val

    # Everything happens here, this is where the type checking is done
    def __add__(self, other : 'Value') -> 'Value':
        if self.type_ == other.type_:
            if (self.val is not None) and (other.val is not None):
                new_val = self.val + other.val
            else:
                # TODO(helq): this should be a new fresh symbol
                new_val = None
            return Value(self.type_, new_val)

        # In any other case, the new Value is unknown
        return Value(type(Any))

    def __radd__(self, other : 'Value') -> 'Value':
        return self.__add__(other)

    def __repr__(self) -> str:
        return 'tl.Value('+repr(self.type_)+', '+repr(self.val)+')'

# TODO(helq): convert Tensor into an abstract class
# class Tensor(Generic[T], metaclass=ABCMeta):
class Tensor(Generic[T]):
    type_ = None # type: Type[T]
    shape = None # type: Tuple[T, ...]
    def __init__(self,
                 type_ : Type[T],
                 shape : 'Tuple[T,...]') -> None:
        self.type_ = type_
        self.shape = shape

    # Everything happens here, this is where the type checking is done
    def __add__(self, other : 'Union[Value, Tensor]') -> 'Tensor':
        if isinstance(other, Value):
            # TODO(helq): the type of the resulting tensor is not the original,
            # but it depends on the value of the variable
            if self.type_ == other.type_:
                return Tensor(self.type_, self.shape)
            else:
                return Tensor(type(Any), self.shape)
        else:
            if self.type_ == other.type_:
                new_type = type(Any)
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
            return Tensor(self.type_, new_shape)

    def __radd__(self, other : 'Union[Value, Tensor]') -> 'Tensor':
        return self.__add__(other)

    # TODO(helq): make this abstract, each class should implement it or use
    # reflection to print the right name always
    def __repr__(self) -> str:
        return 'tl.Tensor('+repr(self.type_)+', '+repr(self.shape)+')'

def for_loop(iterable: Value[Iterable[T]]) -> ValueAsWithStmt[T]:
    # extracting type the elements in the iterable value
    type_elems = iterable.type_.__args__[0].__args__[0] # type: ignore
    return ValueAsWithStmt(Value(type_elems, None))
