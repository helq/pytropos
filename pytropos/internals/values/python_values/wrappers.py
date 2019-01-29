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

__main__ = ['BuiltinMethod']


class BuiltinMethod(AbstractMutVal):
    def __init__(
            self,
            name: 'Optional[str]' = None,
            fun: 'Optional[Callable[[Any, Any, Args, Optional[Pos]], PythonValue]]' = None,
            fun_self: 'Optional[AbstractValue]' = None,
            children: 'Optional[Dict[Any, PythonValue]]' = None
    ) -> None:
        """`fun` has type: `Callable[[AbstractMutVal, Store, Args, Optional[Pos]], PythonValue]`"""
        super().__init__(children=children)

        # print(f"New BuiltinMethod with mut_id {self.mut_id}")

        if not (fun is None or fun_self is None):
            assert name is not None
            self.name = name
            self.fun = fun
            self.children[('attr', '__self__')] = PythonValue(fun_self)
        elif (fun is None) != (fun_self is None):
            raise AttributeError("fun and fun_self must either be set or be None")
        elif children is None:
            self.__im_top = True
            return

        self.__im_top = False

    def __repr__(self) -> str:
        if self.is_top():
            return "BuiltinMethod()"
        return f"BuiltinMethod({self.name!r}, fun={self.fun.__qualname__}," \
               f" fun_self={self.children[('attr', '__self__')]})"

    def __eq__(self, other: Any) -> bool:
        if type(self) is not type(other):
            return False
        if self.is_top() and other.is_top():
            return True
        return super().__eq__(other) and self.name == other.name and self.fun == other.fun

    def fun_call(self, store: Any, args: 'Args', pos: Optional[Pos]) -> PythonValue:
        if self.is_top():
            return PythonValue.top()

        assert isinstance(self.children[('attr', '__self__')].val, AbstractValue), \
            "children['fun_self'] is the original object from which the function has been taken"

        return self.fun(self.children[('attr', '__self__')].val, store, args, pos)

    __top = None  # type: BuiltinMethod

    @classmethod
    def top(cls) -> 'BuiltinMethod':
        if cls.__top is None:
            cls.__top = BuiltinMethod()
        return cls.__top

    def is_top(self) -> 'bool':
        return self.__im_top

    def copy_mut(self,
                 mut_heap: 'Dict[int, PythonValue]'
                 ) -> 'BuiltinMethod':
        new = super().copy_mut(mut_heap)
        # print(f"Copying me, BuiltinMethod, mut_id: {self.mut_id}   new id: {new.mut_id}")
        new.fun = self.fun
        new.name = self.name
        return new  # type: ignore

    def get_attrs(self) -> 'AttrsContainer':
        if self.is_top():
            return AttrsTopContainer()
        return AttrsMutContainer('builtin_function_or_method', self.children, read_only=True)

    def join_mut(self,
                 other: 'BuiltinMethod',
                 mut_heap: 'Dict[Tuple_[str, int], Tuple_[int, int, PythonValue]]',
                 ) -> 'BuiltinMethod':
        new = super().join_mut(other, mut_heap)
        if self.fun is other.fun and self.name == other.name:
            new.fun = self.fun
            new.name = self.name
            return new  # type: ignore
        else:
            return BuiltinMethod.top()

    @property
    def type_name(self) -> str:
        return 'builtin_function_or_method'

    @property
    def abstract_repr(self) -> str:
        if self.is_top():
            return '<built-in method>?'

        assert ('attr', '__self__') in self.children
        fun_self = self.children[('attr', '__self__')]

        if fun_self.is_top():
            return f'<built-in method {self.name} of Top object>'

        assert isinstance(fun_self.val, AbstractValue)
        type_name = fun_self.val.type_name

        return f'<built-in method {self.name} of {type_name} object at _____>'


AcceptedTypes = Union[Tuple_[Type[AbstractValue], ...], Type[AbstractValue]]


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
        # print(f"Copying me, BuiltinMethod, mut_id: {self.mut_id}   new id: {new.mut_id}")
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
        if args.args:
            TypeCheckLogger().new_warning(
                "F001",
                f"Sorry! Pytropos doesn't support calling append with a starred variable",
                pos)
            return PythonValue.top()

        accepted_args = len(self.args) + len(self.kargs)
        total_args = len(args.vals) + len(self.kargs)
        if total_args > accepted_args or total_args < len(self.args):
            TypeCheckLogger().new_warning(
                "E021",
                f"TypeError: TypeError: {self.klass_name}() takes "
                f"from {len(self.args)} to {accepted_args} "
                f"arguments ({total_args} given)",
                pos)
            return PythonValue.top()

        if args.kargs:
            for k, v in args.kargs.items():
                if k in self.kargs:
                    # checking if the arguments are of the right type
                    if not v.is_top() and not isinstance(v.val, self.kargs[k]):
                        assert isinstance(v.val, AbstractValue)
                        TypeCheckLogger().new_warning(
                            "E021",
                            f"TypeError: {self.klass_name}() argument must "
                            f"be ___, not '{v.val.type_name}'",  # TODO(helq): improve error
                            pos)
                        return PythonValue.top()
                else:
                    TypeCheckLogger().new_warning(
                        "E021",
                        f"TypeError: '{k}' is an invalid keyword argument "
                        f"for {self.klass_name}()",
                        pos)
                    return PythonValue.top()

            kargs = args.kargs
        else:
            kargs = {}

        given_values = list(args.vals)
        given_values.extend(kargs.values())
        accepted_types = list(self.args)
        accepted_types.extend(self.kargs.values())
        for v, t in zip(given_values, accepted_types):
            # print(f"v, t: {v}, {t}")
            if not v.is_top() and not isinstance(v.val, t):
                assert isinstance(v.val, AbstractValue)
                TypeCheckLogger().new_warning(
                    "E021",
                    f"TypeError: {self.klass_name}() argument "
                    f"must be ___, not '{v.val.type_name}'",  # TODO(helq): improve error
                    pos)
                return PythonValue.top()

        return PythonValue(self.klass(*args.vals, pos=pos, **kargs))  # type: ignore


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
