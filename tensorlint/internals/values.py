import typing as ty

import operator

__all__ = ['addRules', 'Any', 'Value', 'Int', 'Iterable', 'Float', 'ValueAsWithStmt', 'for_loop']

Pos = ty.Tuple[int,int]

binary_op_methods = ['add', 'radd', 'mul', 'rmul']
special_methods = binary_op_methods

# TODO(helq): make Value an abstract class, no value should be constructible
# from Value
class Value(object):
    __special_methods_implementations = {op: [] for op in binary_op_methods if op[0]!='r'} # type: ty.Any

    def __binop(self, op: str, other: 'Value', pos: ty.Optional[Pos] = None) -> 'ty.Union[Value, NotImplemented]':
        if isinstance(self, Any) or isinstance(other, Any):
            return Any()
        for typeL, typeR, fun in self.__special_methods_implementations[op]:
            # print("vals: {}".format((typeL, typeR, fun)))
            # print("current types: {}  {}".format(type(self), type(other)))
            # print("evaluation: {}  {}".format(type(self), type(other)))
            if isinstance(self, typeL) and isinstance(other, typeR):
                res = fun(self, other, pos)
                if res != NotImplemented:
                    return res
                else:
                    # TODO(helq): show error of implementation. The function
                    # `fun` should implement what it says it should implement,
                    # ie, typeL and typeR
                    print("Function operating between types `{}` and `{}`"
                          " didn't compute. This shouldn't happen!".format(typeL, typeR))
        # TODO(helq): add typechecking error
        # print("The values couldn't be added")
        return NotImplemented
        # TODO(helq): allow continuation of computation, ie, do something to
        # not return NotImplemented (probably, return Any() but add error to
        # list of errors)

    def __add__(self, other: 'Value', pos: ty.Optional[Pos] = None) -> 'Value':
        return self.__binop('add', other, pos)

    def __radd__(self, other, pos = None): # type: ignore # mypy fails if I type it T_T
        return self.__add__(other, pos)

    def __mul__(self, other: 'Value', pos: ty.Optional[Pos] = None) -> 'Value':
        return self.__binop('mul', other, pos)

    def __rmul__(self, other, pos = None): # type: ignore # mypy fails if I type it T_T
        return self.__mul__(other, pos)

# TODO(helq): improve documentation
def addRules(cls: ty.Type) -> ty.Type:
    """
    This decorator adds the rules defined by a class to Value
    """
    def none2cls(t: ty.Optional[ty.Type]) -> ty.Type:
        return cls if t is None else t

    # Modifying original class
    # removing all special method names implemented by
    modified_methods = [] # type: ty.List[str]
    for methodName in special_methods:
        method = '__{}__'.format(methodName)
        if method in cls.__dict__:
            fun = getattr(cls, method)
            getattr(Value, '_Value__special_methods_implementations')[methodName].extend(
                [(cls, none2cls(tR), fun) for tR in cls.add_impls]
            )
            delattr(cls, method)
            modified_methods.append( method )

    print('Methods `{}` added from class `{}` to Value'.format(modified_methods, cls))

    # All methods from Value that weren't implemented are prevent from working
    # in any way
    numeric_methods_ = set(["__{}__".format(v) for v in special_methods])
    notimplemented = numeric_methods_.difference(modified_methods)
    if hasattr(cls, 'impls_inherit'):
        notimplemented = notimplemented.difference( cls.impls_inherit )
    for method in notimplemented:
        def failureMethod(*args, **kargs): # type: ignore
            return NotImplemented

        setattr(cls, method, failureMethod)

    return cls

# TODO(helq): Implement all methods special method names
# https://docs.python.org/3/reference/datamodel.html#special-method-names
class Any(Value):
    def __repr__(self) -> str:
        return "Any()"
    def __call__(self, *args, **kargs) -> 'Any': # type: ignore
        return Any()
    def __getattr__(self, name: str) -> 'Any':
        return Any()
    def __getitem__(self, key: ty.Any) -> 'Any':
        return Any()

@addRules
class Iterable(Value):
    val = None # type: ty.Any
    def __init__(self, val: ty.Any) -> None:
        self.val = val

@addRules
class Str(Value):
    s = None # type: str
    def __init__(self, s: str) -> None:
        self.s = s

# TODO(helq): make `n` and all other variables private
# TODO(helq): trying to set an attribute should throw an error (ie, the
# simulation of the basic building blocks (int, float, ...) should be as close
# as possible to the official libraries)
@addRules
class Int(Value):
    n = None # type: ty.Optional[int]

    add_impls = [None] # type: ty.List[ty.Optional[ty.Type]]
    impls_inherit = ['__radd__']
    def __init__(self, n: ty.Optional[int] = None) -> None:
        self.n = n

    def __binop(self, opname: str, op, other: Value, pos: ty.Optional[Pos] = None): # type: ignore
        if isinstance(other, Int):
            if self.n is None or other.n is None:
                return Int()
            else:
                return Int(op(self.n, other.n))
        return NotImplemented

    def __add__(self, other: Value, pos: ty.Optional[Pos] = None) -> Value:
        return self.__binop('add', operator.add, other, pos) # type: ignore

    def __mul__(self, other: Value, pos: ty.Optional[Pos] = None) -> Value:
        return self.__binop('mul', operator.mul, other, pos) # type: ignore

    def __repr__(self) -> str:
        return "Int("+repr(self.n)+")"

@addRules
class Float(Value):
    n = None # type: ty.Optional[float]
    add_impls = [None, Int] # type: ty.List[ty.Optional[ty.Type]]
    impls_inherit = ['__radd__', '__rmul__']
    def __init__(self, n: ty.Optional[float] = None) -> None:
        self.n = n

    def __binop(self, opname: str, op, other: Value, pos: ty.Optional[Pos] = None): # type: ignore
        if isinstance(other, (Int, Float)):
            if self.n is None or other.n is None:
                return Float()
            else:
                return Float(op(self.n, other.n))
        return NotImplemented

    def __add__(self, other: Value, pos: ty.Optional[Pos] = None) -> Value:
        return self.__binop('add', operator.add, other, pos) # type: ignore

    def __mul__(self, other: Value, pos: ty.Optional[Pos] = None) -> Value:
        return self.__binop('mul', operator.mul, other, pos) # type: ignore

    def __repr__(self) -> str:
        return "Float("+repr(self.n)+")"



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
