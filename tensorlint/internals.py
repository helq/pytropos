from typing import (
    Any, Type, Optional, TypeVar, Generic, List, Tuple, Union
)

__all__ = ['TL_TypeError', 'errors', 'Value', 'Tensor', 'for_loop']

T = TypeVar('T')

class NonImplementedTL(Exception):
    pass

class ValueAsWithStmt(object):
    value = None  # type: Value
    def __init__(self, val: 'Value') -> None:
        self.value = val
    def __enter__(self):
        # type: (...) -> Value
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

class Value(Generic[T]):
    type_ = None # type: Type[T]
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
                new_val = None
            return Value(self.type_, new_val)

        # In any other case, the new Value is unknown
        return Value(type(Any))

    def __radd__(self, other : 'Value') -> 'Value':
        return self.__add__(other)

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
                errors.append( TL_TypeError("The shapes can't be united", -1, -1) )
                exit(0) # :(
            return Tensor(self.type_, new_shape)

    def __radd__(self, other : 'Union[Value, Tensor]') -> 'Tensor':
        return self.__add__(other)

def for_loop(iterable: Any) -> ValueAsWithStmt:
    return ValueAsWithStmt(Value(type(Any), None))
