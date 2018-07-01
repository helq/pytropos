import typing as ty

__all__ = ['Any', 'Value', 'Int', 'Iterable', 'Float', 'ValueAsWithStmt', 'for_loop']

T = ty.TypeVar('T')

class Value(ty.Generic[T]):
    def __getattr__(self, attr : str) -> 'Value':
        return Any()

class Any(Value):
    pass

class Iterable(Value[T]):
    val = None # type: T
    def __init__(self, val: T) -> None:
        self.val = val

class Str(Value):
    s = None # type: str
    def __init__(self, s: str) -> None:
        self.s = s

class Int(Value):
    # TODO(helq): n should be able to save also symbols, for symbolic
    # computation
    n = None # type: ty.Optional[int]
    def __init__(self, n: ty.Optional[int] = None) -> None:
        self.n = n

    # Everything happens here, this is where the type checking is done
    def __add__(self, other : 'Value') -> 'Value':
        if isinstance(other, Int):
            if (self.n is not None) and (other.n is not None):
                n = self.n + other.n # type: ty.Optional[int]
            else:
                # TODO(helq): this should be a new fresh symbol
                n = None
            return Int(n)
        elif isinstance(other, Float):
            if (self.n is not None) and (other.n is not None):
                n_ = self.n + other.n # type: ty.Optional[float]
            else:
                # TODO(helq): this should be a new fresh symbol
                n_ = None
            return Float(n)
        else:
            return Any()

    def __radd__(self, other : 'Value') -> 'Value':
        return self.__add__(other)

    def __repr__(self) -> str:
        return 'tl.Int('+repr(self.n)+')'

class Float(Value):
    n = None # type: ty.Optional[float]
    def __init__(self, n: ty.Optional[float] = None) -> None:
        self.n = n

    # Everything happens here, this is where the type checking is done
    def __add__(self, other : 'Value') -> 'Value':
        if isinstance(other, (Float, Int)):
            if (self.n is not None) and (other.n is not None):
                n = self.n + other.n # type: ty.Optional[float]
            else:
                # TODO(helq): this should be a new fresh symbol
                n = None
            return Float(n)
        else:
            return Any()

    def __radd__(self, other : 'Value') -> 'Value':
        return self.__add__(other)

    def __repr__(self) -> str:
        return 'tl.Int('+repr(self.n)+')'



class ValueAsWithStmt(object):
    value = None  # type: Int
    def __init__(self, val: 'Int') -> None:
        self.value = val
    def __enter__(self):
        # type: (...) -> Int
        return self.value
    def __exit__(self, exc_type, exc_value, traceback # type: ignore
                 ) -> None:
        pass

def for_loop(iterable: Iterable) -> ValueAsWithStmt:
    # extracting type the elements in the iterable value
    # type_elems = iterable.type_.__args__[0].__args__[0] # type: ignore
    return ValueAsWithStmt(Int(None))
