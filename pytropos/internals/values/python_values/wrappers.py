from abc import abstractmethod
from typing import (
    Type, List as List_, Dict, Optional, Any, Tuple as Tuple_, Callable, Union
)

from ..abstract_value import AbstractValue
from .python_values import (
    PythonValue, Args, AbstractMutVal, AttrsContainer,
    AttrsMutContainer, AttrsTopContainer
)
from ...errors import TypeCheckLogger

from ...miscelaneous import Pos

__main__ = ['BuiltinFun']


# A BuiltinFun or BuiltinClass accepts args of type (eg, (Int, Tuple)) and single values
# (eg, List)
AcceptedTypes = Union[Tuple_[Type[AbstractValue], ...], Type[AbstractValue]]


# TODO(helq): Check if there is some collision between args.vals and args.kargs
def check_fun_args_kargs(  # noqa: C901
        fun_name: str,
        args: 'Args',
        self_args: List_[AcceptedTypes],
        self_kargs: Dict[str, AcceptedTypes],
        pos: Optional[Pos]
) -> 'Optional[Dict[str, PythonValue]]':
    if args.args is not None:
        TypeCheckLogger().new_warning(
            "F001",
            f"Sorry! Pytropos doesn't support calling append with a starred variable",
            pos)
        return None

    accepted_args = len(self_args) + len(self_kargs)
    total_args = len(args.vals) + len(self_kargs)
    if total_args > accepted_args or total_args < len(self_args):
        if not self_kargs:
            if accepted_args == 0:
                num = "no arguments"
            elif accepted_args == 1:
                num = "exactly one argument"
            else:
                num = "exactly {accepted_args} arguments"
        else:
            num = f"from {len(self_args)} to {accepted_args} arguments"

        TypeCheckLogger().new_warning(
            "E014",
            f"TypeError: {fun_name}() takes {num} ({total_args} given)",
            pos)
        return None

    if args.kargs:
        if len(self_kargs) == 0:
            TypeCheckLogger().new_warning(
                "E014",
                f"TypeError: {fun_name}() takes no keyword arguments",
                pos)
            return None
        for k, v in args.kargs.items():
            if k in self_kargs:
                # checking if the arguments are of the right type
                if not v.is_top() and not isinstance(v.val, self_kargs[k]):
                    assert isinstance(v.val, AbstractValue)
                    TypeCheckLogger().new_warning(
                        "E021",
                        f"TypeError: {fun_name}() argument must "
                        f"be {name_of_types(self_kargs[k])}, not '{v.val.type_name}'",
                        pos)
                    return None
            else:
                TypeCheckLogger().new_warning(
                    "E021",
                    f"TypeError: '{k}' is an invalid keyword argument "
                    f"for {fun_name}()",
                    pos)
                return None

        kargs = args.kargs
    else:
        kargs = {}

    given_values = list(args.vals)
    given_values.extend(kargs.values())
    accepted_types = list(self_args)
    accepted_types.extend(self_kargs.values())
    for v, t in zip(given_values, accepted_types):
        # print(f"v, t: {v}, {t}")
        if not v.is_top() and not isinstance(v.val, t):
            assert isinstance(v.val, AbstractValue)
            TypeCheckLogger().new_warning(
                "E021",
                f"TypeError: {fun_name}() argument "
                f"must be {name_of_types(t)}, not '{v.val.type_name}'",
                pos)
            return None

    return kargs


# TODO(helq): use something less hacky than running type_name.fget with None
def name_of_types(types: AcceptedTypes) -> str:
    if isinstance(types, tuple):
        tys_str = []  # type: List_[str]
        for t in types:
            tys_str.append(t.type_name.fget(None))  # type: ignore
        return '(' + ', '.join(tys_str) + ')'
    else:
        return types.type_name.fget(None)  # type: ignore


class BuiltinFun(AbstractMutVal):
    def __init__(
            self,
            name: 'Optional[str]' = None,
            fun: 'Optional[Callable[..., PythonValue]]' = None,
            fun_self: 'Optional[AbstractValue]' = None,
            args: Optional[List_[AcceptedTypes]] = None,
            kargs: Optional[Dict[str, AcceptedTypes]] = None,
            children: 'Optional[Dict[Any, PythonValue]]' = None
    ) -> None:
        """Wraps a method into an AbstractMutVal.

        You must define the type of the input arguments (and kargs)"""
        super().__init__(children=children)

        # print(f"New BuiltinFun with mut_id {self.mut_id}")

        if fun is not None:
            assert name is not None
            self.name = name
            self.fun = fun
            self.args = [] if args is None else args
            self.kargs = {} if kargs is None else kargs
            if fun_self is None:
                self.is_method = False
            else:
                self.is_method = True
                self.children[('attr', '__self__')] = PythonValue(fun_self)
        elif children is None:
            self.__im_top = True
            return

        self.__im_top = False

    def __repr__(self) -> str:
        if self.is_top():
            return "BuiltinFun()"
        if self.is_method:
            return f"BuiltinFun({self.name!r}, fun={self.fun.__qualname__}," \
                   f" fun_self={self.children[('attr', '__self__')]})"
        return f"BuiltinFun({self.name!r}, fun={self.fun.__qualname__}, fun_self=None)"

    def __eq__(self, other: Any) -> bool:
        if type(self) is not type(other):
            return False
        if self.is_top() and other.is_top():
            return True
        return super().__eq__(other) \
            and self.name == other.name \
            and self.fun == other.fun \
            and self.is_method == self.is_method

    def fun_call(self, store: Any, args: 'Args', pos: Optional[Pos]) -> PythonValue:
        if self.is_top():
            return PythonValue.top()

        kargs = check_fun_args_kargs(self.name, args, self.args, self.kargs, pos)
        if kargs is None:
            return PythonValue.top()

        if self.is_method:
            fun_self = self.children[('attr', '__self__')].val
            assert isinstance(fun_self, AbstractValue), \
                "children['fun_self'] is the original object from which the function has been taken"

            return self.fun(fun_self, *args.vals, pos=pos, **kargs)
        else:
            return self.fun(*args.vals, pos=pos, **kargs)

    __top = None  # type: BuiltinFun

    @classmethod
    def top(cls) -> 'BuiltinFun':
        if cls.__top is None:
            cls.__top = BuiltinFun()
        return cls.__top

    def is_top(self) -> 'bool':
        return self.__im_top

    def copy_mut(self,
                 mut_heap: 'Dict[int, PythonValue]'
                 ) -> 'BuiltinFun':
        new = super().copy_mut(mut_heap)
        # print(f"Copying me, BuiltinFun, mut_id: {self.mut_id}   new id: {new.mut_id}")
        new.fun = self.fun
        new.name = self.name
        new.is_method = self.is_method
        new.args = self.args
        new.kargs = self.kargs
        return new  # type: ignore

    def get_attrs(self) -> 'AttrsContainer':
        if self.is_top():
            return AttrsTopContainer()
        return AttrsMutContainer('builtin_function_or_method', self.children, read_only=True)

    def join_mut(self,
                 other: 'BuiltinFun',
                 mut_heap: 'Dict[Tuple_[str, int], Tuple_[int, int, PythonValue]]',
                 ) -> 'BuiltinFun':
        new = super().join_mut(other, mut_heap)
        if self.fun is other.fun and self.name == other.name:
            new.fun = self.fun
            new.name = self.name
            new.is_method = self.is_method
            new.args = self.args
            new.kargs = self.kargs
            return new  # type: ignore
        else:
            return BuiltinFun.top()

    @property
    def type_name(self) -> str:
        return 'builtin_function_or_method'

    @property
    def abstract_repr(self) -> str:
        if self.is_top():
            return '<built-in method>?'

        if self.is_method:
            assert ('attr', '__self__') in self.children
            fun_self = self.children[('attr', '__self__')]

            if fun_self.is_top():
                return f'<built-in method {self.name} of Top object>'

            assert isinstance(fun_self.val, AbstractValue)
            type_name = fun_self.val.type_name

            return f'<built-in method {self.name} of {type_name} object at _____>'
        else:
            return f'<built-in function {self.name}>'


class BuiltinClass(AbstractMutVal):
    def __init__(
            self,
            klass_name: Optional[str] = None,
            klass: Optional[Type[AbstractMutVal]] = None,
            args: Optional[List_[AcceptedTypes]] = None,
            kargs: Optional[Dict[str, AcceptedTypes]] = None,
            children: 'Optional[Dict[Any, PythonValue]]' = None
    ) -> None:
        super().__init__(children=children)

        if klass is not None:
            assert klass_name is not None
            self.klass_name = klass_name
            self.klass = klass
            self.args = [] if args is None else args
            self.kargs = {} if kargs is None else kargs
        elif children is None:
            self.__im_top = True
            return

        self.__im_top = False

    def __repr__(self) -> str:
        if self.is_top():
            return "BuiltinClass()"
        args_to_str = [('('+', '.join(c_.__name__ for c_ in c)+')'
                        if isinstance(c, tuple)
                        else c.__name__)
                       for c in self.args]
        return f"BuiltinClass({self.klass_name!r}, klass={self.klass.__qualname__}," \
               f" args=[{', '.join(str(c) for c in args_to_str)}]," \
               f" kargs={self.kargs})"

    def __eq__(self, other: Any) -> bool:
        if type(self) is not type(other):
            return False
        if self.is_top() and other.is_top():
            return True
        return super().__eq__(other) \
            and self.klass_name == other.klass_name \
            and self.klass == other.klass \
            and self.args == other.args \
            and self.kargs == other.kargs

    def class_top(self) -> 'PythonValue':
        if self.is_top():
            return PythonValue.top()
        return PythonValue(self.klass.top())

    __top = None  # type: BuiltinClass

    @classmethod
    def top(cls) -> 'BuiltinClass':
        if cls.__top is None:
            cls.__top = BuiltinClass()
        return cls.__top

    def is_top(self) -> bool:
        return self.__im_top

    @property
    def type_name(self) -> str:
        return "type"

    @property
    def abstract_repr(self) -> str:
        if self.is_top():
            return '<class ___>?'
        try:
            return f"<class '{self.type_name}'>"
        except:  # noqa: E722
            return '<class ___>'

    def copy_mut(self,
                 mut_heap: 'Dict[int, PythonValue]'
                 ) -> 'BuiltinClass':
        new = super().copy_mut(mut_heap)  # type: BuiltinClass
        # print(f"Copying me, BuiltinFun, mut_id: {self.mut_id}   new id: {new.mut_id}")
        if self.is_top():
            return self

        new.klass_name = self.klass_name
        new.klass = self.klass
        new.args = self.args
        new.kargs = self.kargs
        return new

    def join_mut(self,
                 other: 'BuiltinClass',
                 mut_heap: 'Dict[Tuple_[str, int], Tuple_[int, int, PythonValue]]',
                 ) -> 'BuiltinClass':
        new = super().join_mut(other, mut_heap)
        if self.is_top() or other.is_top():
            return self.top()
        if self.klass is other.klass \
                and self.args == other.args \
                and self.kargs == other.kargs:
            new.klass_name = self.klass_name
            new.klass = self.klass
            new.args = self.args
            new.kargs = self.kargs
            return new  # type: ignore
        else:
            return BuiltinClass.top()

    def get_attrs(self) -> 'AttrsContainer':
        if self.is_top():
            return AttrsTopContainer()
        return AttrsMutContainer('builtin class', self.children, read_only=True)

    def fun_call(self, store: Any, args: 'Args', pos: Optional[Pos]) -> PythonValue:
        if self.is_top():
            return PythonValue.top()

        kargs = check_fun_args_kargs(self.klass_name, args, self.args, self.kargs, pos)
        if kargs is None:
            return PythonValue.top()

        return PythonValue(self.klass(*args.vals, pos=pos, **kargs))  # type: ignore


# TODO(helq): improve attr warning to say something like: "AttributeError: module '---'
# has no attribute '---'"
class BuiltinModule(AbstractMutVal):
    def __init__(
            self,
            mod_name: 'Optional[str]' = None,
            funcs: 'Optional[Dict[str, AbstractValue]]' = None,
            read_only: bool = False,
            children: 'Optional[Dict[Any, PythonValue]]' = None
    ) -> None:
        super().__init__(children)

        if funcs is not None:
            assert mod_name is not None
            for key, val in funcs.items():
                self.children[('attr', key)] = PythonValue(val)
            self.read_only = read_only
            self.mod_name = mod_name
        elif children is None:
            self.__im_top = True
            return

        self.__im_top = False

    def __repr__(self) -> str:
        if self.is_top():
            return "BuiltinModule()"
        return f"BuiltinModule({self.mod_name!r}," \
               f" funcs={ {k[1]: v.val for k, v in self.children.items() if k[0]=='attr'} }," \
               f" read_only={self.read_only})"

    def __eq__(self, other: Any) -> bool:
        if type(self) is not type(other):
            return False
        if self.is_top() and other.is_top():
            return True
        return super().__eq__(other) \
            and self.read_only == other.read_only \
            and self.mod_name == other.mod_name

    __top = None  # type: BuiltinModule

    @classmethod
    def top(cls) -> 'BuiltinModule':
        if cls.__top is None:
            cls.__top = BuiltinModule()
        return cls.__top

    def is_top(self) -> 'bool':
        return self.__im_top

    def copy_mut(self,
                 mut_heap: 'Dict[int, PythonValue]'
                 ) -> 'BuiltinModule':
        new = super().copy_mut(mut_heap)  # type: BuiltinModule
        if self.is_top():
            return self

        new.read_only = self.read_only
        new.mod_name = self.mod_name
        return new

    def join_mut(self,
                 other: 'BuiltinModule',
                 mut_heap: 'Dict[Tuple_[str, int], Tuple_[int, int, PythonValue]]',
                 ) -> 'BuiltinModule':
        new = super().join_mut(other, mut_heap)  # type: BuiltinModule
        if self.is_top() or other.is_top():
            return self.top()
        if self.read_only == other.read_only \
                and self.mod_name == other.mod_name:
            new.read_only = self.read_only
            new.mod_name = self.mod_name
            return new
        else:
            return BuiltinModule.top()

    @property
    def abstract_repr(self) -> 'str':
        if self.is_top():
            return f"<module 'XXXX' from 'YYYY'>?"
        return f"<module '{self.mod_name}' from 'YYYY'>"

    @property
    def type_name(self) -> str:
        return "module"


class BuiltinType(AbstractMutVal):
    """Used for Annotations (type hints)"""

    @abstractmethod
    def get_absvalue(self) -> 'PythonValue':
        """Returns the python value that the annotation stores"""
        raise NotImplementedError()
