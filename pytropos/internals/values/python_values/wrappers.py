from typing import Any, Optional, Callable
from typing import Dict, Tuple  # noqa: F401

from ..abstract_value import AbstractValue
from .python_values import PythonValue, Args, AbstractMutVal, AttrsContainer, AttrsMutContainer

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
        """`fun` has type: `Callable[[Any, Args, Optional[Pos]], PythonValue]`"""
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
        return AttrsMutContainer('builtin_function_or_method', self.children, read_only=True)

    def join_mut(self,
                 other: 'BuiltinMethod',
                 mut_heap: 'Dict[Tuple[str, int], Tuple[int, int, PythonValue]]',
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
