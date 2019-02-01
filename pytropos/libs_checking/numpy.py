import math
from typing import (
    Dict, Optional, Any, Tuple as Tuple_, Union,
)
from typing import List as List_  # noqa: F401

from ..internals.values.python_values.python_values import (
    AbstractMutVal, PythonValue, AttrsContainer, AttrsMutContainer,
    AttrsTopContainer
)
from ..internals.values.abstract_value import AbstractValue
from ..internals.values.builtin_values import Int
import pytropos.internals.values as pv
from ..internals.values.python_values.builtin_mutvalues import Tuple, List
from ..internals.values.python_values.wrappers import (
    BuiltinClass, BuiltinModule, BuiltinFun
)
from ..internals.errors import TypeCheckLogger

from ..internals.miscelaneous import Pos


class NdArray(AbstractMutVal):
    def __init__(  # noqa: C901
            self,
            shape: 'Union[PythonValue, Tuple, None]' = None,
            pos: 'Optional[Pos]' = None,
            children: 'Optional[Dict[Any, PythonValue]]' = None
    ) -> None:
        super().__init__(children=children)
        if shape is not None:
            if isinstance(shape, PythonValue) and not shape.is_top():
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

            elif isinstance(shape, Tuple):
                shape = PythonValue(shape)
            else:  # shape.is_top()
                self._im_top = True
                return

            self.children['shape'] = shape

            # self.children[('attr', 'dot')] = \
            #     PythonValue(BuiltinFun(
            #         'dot',
            #         NdArray._method_dot,
            #         self,
            #         args=[AbstractValue]
            #     ))

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

    # def _method_dot(self, other: 'PythonValue', pos: Optional[Pos]) -> 'PythonValue':
    #     if self.is_top() or other.is_top():
    #         return PythonValue.top()

    #     other_array = _function_array(other, pos)
    #     if other_array.is_top():
    #         new_array = self.top()
    #     else:
    #         assert isinstance(other_array.val, NdArray)
    #         # COMPLETE_ME ...  # CHECKING HERE!!! COMPLETE ME!!!
    #     return PythonValue(new_array)


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


def _function_zero(val: PythonValue, pos: Optional[Pos]) -> PythonValue:
    return PythonValue(NdArray(val, pos))


def getshape_list(lst: Union[List, Tuple]) -> 'Tuple':  # noqa: C901
    if lst.is_top():
        return Tuple.top()  # type: ignore

    shape = {}  # type: Dict[Tuple_[str, int], PythonValue]
    is_there_top = False

    indices = lst.sorted_indices()

    if lst.size[0] != lst.size[1]:
        shape['index', 0] = PythonValue(Int.top())
        is_there_top = True
    else:
        shape['index', 0] = PythonValue(Int(lst.size[0]))
        if len(indices) != lst.size[0]:
            is_there_top = True

    # print(f"showing indexes {indices}")

    shape_values = []  # type: List_[Tuple]
    for _, val in indices:
        if val.is_top():
            is_there_top = True
        else:
            absval = val.val
            assert isinstance(absval, AbstractValue)
            shape_val = getshape(absval)  # type: Optional[Tuple]
            if shape_val is None:
                is_there_top = True
            else:
                shape_values.append(shape_val)

    all_same_shape = True
    all_dim_eq = True
    if shape_values:
        shape_val = shape_values[0]
        for shape_val_other in shape_values[1:]:
            if shape_val != shape_val_other:
                shape_val = shape_val.join_mut(shape_val_other, {})  # type: ignore

            any_dim_eq = False
            for i, val in shape_val.sorted_indices():  # type: ignore
                if val.is_top() or (
                        isinstance(val.val, Int) and val.val.is_top()
                ):
                    all_dim_eq = False
                    break
                else:
                    any_dim_eq = True

            if not any_dim_eq:
                all_same_shape = False
    else:
        shape_val = None

    if is_there_top:
        theshape = Tuple(children=shape)
        if all_same_shape:
            theshape.size = (1, math.inf)
        else:
            theshape.size = (1, 1)
    else:
        if all_same_shape and shape_val is None:
            # there were no shapes to analyse, the list is empty
            theshape = Tuple([PythonValue(Int(0))])
        else:  # We know for sure that shape_val is not None
            assert shape_val is not None
            for i, val in shape_val.sorted_indices():
                if val.is_top() or (
                        isinstance(val.val, Int) and val.val.is_top()
                ):
                    break
                else:
                    shape['index', i+1] = val  # val is always Int

            theshape = Tuple(children=shape)
            if all_dim_eq:
                theshape.size = (shape_val.size[0]+1, shape_val.size[1]+1)
            else:
                theshape.size = (i+1, i+1)

    # print(f"showing shape {theshape}")
    return theshape


def getshape(absval: AbstractValue) -> 'Optional[Tuple]':
    if isinstance(absval, Int):
        return Tuple([])
    elif isinstance(absval, (List, Tuple)):
        return getshape_list(absval)
    elif isinstance(absval, NdArray):
        assert isinstance(absval.children['shape'].val, Tuple)
        return absval.children['shape'].val

    # TODO(helq): add more checks for all other variables that numpy supports
    # https://stackoverflow.com/questions/40378427/numpy-formal-definition-of-array-like-objects
    else:
        return None


def _function_array(val: PythonValue, pos: Optional[Pos]) -> PythonValue:
    """Takes any PythonValu and tries to convert it into a NdArray.

    Returns either a NdArray or a pv.Top"""

    if val.is_top():
        return PythonValue.top()

    absval = val.val
    assert isinstance(absval, AbstractValue)
    shape = getshape(absval)

    if shape is None:
        return PythonValue.top()
    return PythonValue(NdArray(shape, pos))


ndarray = BuiltinClass(
    'ndarray', NdArray,
    args=[(Tuple, Int, List)],
    # kargs={'dtype': AbstractValue,
    #        'buffer': AbstractValue,
    #        'offset': AbstractValue,
    #        'strides': AbstractValue,
    #        'order': AbstractValue}
)

array = BuiltinFun(
    'array', _function_array, args=[AbstractValue],
)
zeros = BuiltinFun(
    'zeros', _function_zero, args=[(Tuple, Int, List)],
)
ones = BuiltinFun(
    'ones', _function_zero, args=[(Tuple, Int, List)],
)

numpy_module = PythonValue(BuiltinModule(
    'numpy', {
        'ndarray': ndarray,
        'array': array,
        'zeros': zeros,
        'ones': ones,
    }
))
