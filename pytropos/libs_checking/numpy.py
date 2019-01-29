from typing import (
    Dict, Optional, Any, Tuple as Tuple_,
    Union
)

from ..internals.values.python_values.python_values import (
    AbstractMutVal, PythonValue, AttrsContainer, AttrsMutContainer,
    AttrsTopContainer
)
from ..internals.values.abstract_value import AbstractValue
from ..internals.values.builtin_values import Int
import pytropos.internals.values as pv
from ..internals.values.python_values.builtin_mutvalues import Tuple, List
from ..internals.values.python_values.wrappers import (
    BuiltinClass, BuiltinModule
)
from ..internals.errors import TypeCheckLogger

from ..internals.miscelaneous import Pos


class NdArray(AbstractMutVal):
    def __init__(
            self,
            shape: 'Optional[PythonValue]' = None,
            pos: 'Optional[Pos]' = None,
            children: 'Optional[Dict[Any, PythonValue]]' = None
    ) -> None:
        super().__init__(children=children)
        if shape is not None and not shape.is_top():
            # We have warrantied from BuiltinClass that this shape.val is either:
            # - Tuple
            # - List
            # - Int
            # - 'PT.Top'
            assert isinstance(shape.val, (Tuple, Int, List))
            if isinstance(shape.val, Int):
                shape = PythonValue(Tuple([shape]))
            elif isinstance(shape.val, List):
                shape = PythonValue(Tuple.fromList(shape.val))
            elif shape.is_top():
                shape = PythonValue(Tuple.top())

            assert isinstance(shape.val, Tuple)

            for k in shape.val.children:
                if isinstance(k, tuple) and k[0] == 'index':
                    value = shape.val.children[k]
                    if value.is_top():
                        shape.val.children[k] = pv.Top
                    elif not isinstance(value.val, Int):
                        assert isinstance(value.val, AbstractValue)
                        TypeCheckLogger().new_warning(
                            "E017",
                            f"TypeError: '{value.val.type_name}' object cannot"
                            " be interpreted as an integer",
                            pos)
                        shape.val.children[k] = pv.int()

            self.children['shape'] = shape

            # self.children[('attr', 'dot')] = \
            #     PythonValue(BuiltinMethod('dot', NdArray._method_dot, self))

        elif children is None:  # shape is None and children is None
            self._im_top = True
            return

        self._im_top = False

    def __repr__(self) -> str:
        if self.is_top():
            return "NdArray()"
        return f"NdArray({self.children['shape']})"

    def __eq__(self, other: Any) -> 'bool':
        if not type(other) is type(self):
            return False
        if self.is_top() and other.is_top():
            return True
        return super().__eq__(other)

    __top = None  # type: NdArray

    @classmethod
    def top(cls) -> 'NdArray':
        if cls.__top is None:
            cls.__top = cls()
        return cls.__top

    def is_top(self) -> 'bool':
        return self._im_top

    def copy_mut(self,
                 mut_heap: 'Dict[int, PythonValue]'
                 ) -> 'NdArray':
        if self.is_top():
            return self
        return super().copy_mut(mut_heap)  # type: ignore

    def join_mut(self,
                 other: 'NdArray',
                 mut_heap: 'Dict[Tuple_[str, int], Tuple_[int, int, PythonValue]]',
                 ) -> 'NdArray':
        assert type(self) is type(other)
        new = super().join_mut(other, mut_heap)
        if self.is_top() or other.is_top():
            return self.top()
        return new  # type: ignore

    @property
    def abstract_repr(self) -> 'str':
        if self.is_top():
            return 'array?'
        return f'array(shape={self.children["shape"]})'

    @property
    def type_name(self) -> str:
        return "numpy.ndarray"

    def get_attrs(self) -> 'AttrsContainer':
        if self.is_top():
            return AttrsTopContainer()
        return AttrsNdArrayContainer('ndarray', self.children, read_only=True)


class AttrsNdArrayContainer(AttrsMutContainer):
    def __getitem__(self, key_: 'Union[str, Tuple_[str, Pos]]') -> PythonValue:
        if not isinstance(key_, tuple):
            key = key_
            src_pos = None  # type: Optional[Pos]
        else:
            key, src_pos = key_

        if key is 'shape':
            assert isinstance(self.children['shape'].val, Tuple)
            # This is safe because shape should be a tuple with only integer values
            return self.children['shape'].copy_mut({})

        return super().__getitem__(key_)


ndarray = BuiltinClass(
    'ndarray', NdArray, args=[(Tuple, Int, List)],
    # kargs={'dtype': AbstractValue,
    #        'buffer': AbstractValue,
    #        'offset': AbstractValue,
    #        'strides': AbstractValue,
    #        'order': AbstractValue}
)

numpy_module = PythonValue(BuiltinModule(
    'numpy', {
        'ndarray': ndarray
    }
))
