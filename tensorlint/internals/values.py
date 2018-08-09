import typing as ty

import operator

__all__ = ['addRules', 'Any', 'Value', 'Int', 'Iterable', 'Float', 'ValueAsWithStmt', 'for_loop']

Pos = ty.Tuple[int, int]

BINARY_OP_METHODS = ['add', 'radd', 'mul', 'rmul']
SPECIAL_METHODS = BINARY_OP_METHODS

OperationFun = ty.Callable[['Value', 'Value', ty.Optional[Pos]], 'Value']
OperationTupleTypes = ty.Tuple[ty.Type, ty.Type, OperationFun]

special_methods_implementations: ty.Dict[str, ty.List[OperationTupleTypes]] = \
    {op: [] for op in BINARY_OP_METHODS if op[0] != 'r'}


# TODO(helq): make Value an abstract class, no value should be constructible
# from Value
class Value(object):
    """
    All variables in tensorlint must derivate from `Value`. `Value` is just like `object`
    for all objects in python.

    `Value` implements the general (gradual) type checking rules.
    """


# TODO(helq): improve documentation
def addRules(debug: bool = False) -> ty.Callable[[ty.Type], ty.Type]:
    def deco(cls: ty.Type) -> ty.Type:
        """
        This decorator adds the rules defined by a class to Value
        """
        def none2cls(t: ty.Optional[ty.Type]) -> ty.Type:
            return cls if t is None else t

        # Modifying original class
        # removing all special method names implemented by
        modified_methods = []  # type: ty.List[str]
        for method_name in SPECIAL_METHODS:
            method = '__{}__'.format(method_name)
            if method in cls.__dict__:
                fun = getattr(cls, method)
                special_methods_implementations[method_name].extend(
                    [(cls, none2cls(tR), fun) for tR in cls.add_impls]
                )
                delattr(cls, method)
                modified_methods.append(method)

        if debug:
            print('Methods `{}` added from class `{}` to Value'.format(modified_methods, cls))

        # All methods from Value that weren't implemented are prevent from working
        # in any way
        numeric_methods_ = set(["__{}__".format(v) for v in SPECIAL_METHODS])
        notimplemented = numeric_methods_.difference(modified_methods)
        for method in notimplemented:
            def failure_method(*args, **kargs):  # type: ignore
                """I'm here to prevent you to perform the operation"""
                return NotImplemented

            setattr(cls, method, failure_method)

        return cls
    return deco


# TODO(helq): Implement all methods special method names
# https://docs.python.org/3/reference/datamodel.html#special-method-names
class Any(Value):
    error_when_used = False

    def checkErrorIfUsed(self) -> None:
        if Any.error_when_used:
            raise Exception("Trying to use Any value")

    def __init__(self, *args: ty.Any, **kargs: ty.Any) -> None:
        if len(args) > 0:
            if Any.error_when_used:
                raise Exception("Trying to construct Any value (with parms: {})".format(repr(args)))
        if Any.error_when_used:
            raise Exception("Trying to construct Any value")

    def __repr__(self) -> str:
        return "Any()"

    def __call__(self, *args, **kargs) -> 'Any':  # type: ignore
        return Any()

    def __getattr__(self, name: str) -> 'Any':
        return Any()

    def __getitem__(self, key: ty.Any) -> 'Any':
        return Any()


@addRules()
class Iterable(Value):
    val = None  # type: ty.Any

    def __init__(self, val: ty.Any) -> None:
        self.val = val


@addRules()
class Str(Value):
    s = None  # type: str

    def __init__(self, s: str) -> None:
        self.s = s


# TODO(helq): make `n` and all other variables private
# TODO(helq): trying to set an attribute should throw an error (ie, the
# simulation of the basic building blocks (int, float, ...) should be as close
# as possible to the official libraries)
@addRules()
class Int(Value):
    n = None  # type: ty.Optional[int]
    add_impls = [None]  # type: ty.List[ty.Optional[ty.Type]]

    def __init__(self, n: ty.Optional[int] = None) -> None:
        self.n = n

    def __binop(self, op, other: Value, src_pos: ty.Optional[Pos] = None):  # type: ignore
        if isinstance(other, Int):
            if self.n is None or other.n is None:
                return Int()
            return Int(op(self.n, other.n))
        return NotImplemented

    def __add__(self, other: Value, src_pos: ty.Optional[Pos] = None) -> Value:
        return self.__binop(operator.add, other, src_pos)  # type: ignore

    def __mul__(self, other: Value, src_pos: ty.Optional[Pos] = None) -> Value:
        return self.__binop(operator.mul, other, src_pos)  # type: ignore

    def __repr__(self) -> str:
        return "Int("+repr(self.n)+")"

    def __eq__(self, other: Value, src_pos: ty.Optional[Pos] = None) -> Value:  # type: ignore
        return self.__binop(operator.eq, other, src_pos)  # type: ignore


# TODO(helq): add warning when operating with nan values
@addRules()
class Float(Value):
    n = None  # type: ty.Optional[float]
    add_impls = [None, Int]  # type: ty.List[ty.Optional[ty.Type]]

    def __init__(self, n: ty.Optional[float] = None) -> None:
        self.n = n

    def __binop(self, op, other: Value, src_pos: ty.Optional[Pos] = None):  # type: ignore
        if isinstance(other, (Int, Float)):
            if self.n is None or other.n is None:
                return Float()
            else:
                return Float(op(self.n, other.n))
        return NotImplemented

    def __add__(self, other: Value, src_pos: ty.Optional[Pos] = None) -> Value:
        return self.__binop(operator.add, other, src_pos)  # type: ignore

    def __mul__(self, other: Value, src_pos: ty.Optional[Pos] = None) -> Value:
        return self.__binop(operator.mul, other, src_pos)  # type: ignore

    def __repr__(self) -> str:
        return "Float("+repr(self.n)+")"


class ValueAsWithStmt(object):
    value = None  # type: Int

    def __init__(self, val: 'Int') -> None:
        self.value = val

    def __enter__(self):
        # type: (...) -> Int
        return self.value

    def __exit__(self, exc_type, exc_value, traceback  # type: ignore
                 ) -> None:
        pass


def for_loop(iterable: Iterable) -> ValueAsWithStmt:
    # extracting type the elements in the iterable value
    # type_elems = iterable.type_.__args__[0].__args__[0] # type: ignore
    return ValueAsWithStmt(Int(None))
