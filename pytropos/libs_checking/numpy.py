import math
import re
from typing import Dict, Optional, Any, Tuple as Tuple_, Union
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


extract_op = re.compile(r'op_([a-zA-Z]*)(_([a-zA-Z]*))?$')


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
        self.non_mut_attrs = {
            'shape': self._attr_shape,
            'ndim': self._attr_ndim,
        }

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
        return AttrsMutContainer('ndarray', self.children, self.non_mut_attrs, read_only=True)

    @property
    def shape(self) -> 'Tuple':
        assert not self.is_top(), "Only non Top values have shape"
        assert isinstance(self.children['shape'].val, Tuple)
        return self.children['shape'].val

    _supported_ops = {
        'add', 'sub', 'mul', 'radd', 'rsub', 'rmul',
        'truediv', 'floordiv', 'mod', 'rtruediv', 'rfloordiv', 'rmod'
    }

    def __getattribute__(self, name: str) -> Any:
        # Checking if name is 'op_OP' (eg, 'op_add')
        op = extract_op.match(name)
        if op and op[1] in NdArray._supported_ops:  # accepting op_add and op_add_TYPE
            if op[3] is None:
                return object.__getattribute__(self, 'op_OP')
            else:
                return object.__getattribute__(self, 'op_OP_Any')

        return object.__getattribute__(self, name)

    def op_OP_Any(self,
                  other: 'AbstractValue',
                  pos: 'Optional[Pos]'
                  ) -> 'Optional[NdArray]':
        if isinstance(other, NdArray):
            return self.op_OP(other, pos)

        other_array = array_from_AbstractValue(other, pos)

        if other_array is None:
            return None
        else:
            return self.op_OP(other_array, pos)

    def op_OP(self, other: 'NdArray', pos: 'Optional[Pos]') -> 'NdArray':
        if self.is_top():
            return other.copy_mut({})
        elif other.is_top():
            return self.copy_mut({})

        new_shape = _broadcast(self.shape, other.shape, pos)
        if new_shape is None:
            return NdArray.top()
        else:
            return NdArray(new_shape)

    def _attr_shape(self) -> 'PythonValue':
        assert isinstance(self.children['shape'].val, Tuple)
        # This is safe because shape should be a tuple with only integer values
        return self.children['shape'].copy_mut({})

    def _attr_ndim(self) -> 'PythonValue':
        shape = self.children['shape'].val
        assert isinstance(shape, Tuple)

        if shape.is_size_determined():
            return PythonValue(Int(shape.size[0]))
        else:
            return PythonValue(Int.top())

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


def _function_zero(val: PythonValue, pos: Optional[Pos]) -> PythonValue:
    return PythonValue(NdArray(val, pos))


def __dims_from_Tuple(tpl: Tuple, size: int) -> 'List_[Int]':
    """Returns all the values from the tuple in order.

    Assumptions:

    - All elements in the Tuple are Int's (they come from a NdArray)
    - tpl.size[0] == tpl.size[1]
    - size >= tpl.size[1]"""

    lst: 'List_[Int]'
    lst = [None]*size  # type: ignore

    shift = size - tpl.size[0]

    for i, dim in tpl.sorted_indices():
        assert isinstance(dim.val, Int)
        lst[i + shift] = dim.val

    for i in range(size):
        if lst[i] is None:
            lst[i] = Int.top()

    return lst


def _broadcast(left: Tuple, right: Tuple, pos: 'Optional[Pos]') -> 'Optional[Tuple]':
    if not left.is_size_determined() \
            or not right.is_size_determined():
        return None

    dims_size = max(left.size[0], right.size[0])

    left_dims = __dims_from_Tuple(left, dims_size)
    right_dims = __dims_from_Tuple(right, dims_size)

    new_shape = []  # type: List_[PythonValue]
    for ldim, rdim in zip(left_dims, right_dims):
        if ldim == rdim:
            new_shape.append(PythonValue(ldim))
        elif ldim.is_top():
            new_shape.append(PythonValue(rdim))
        elif rdim.is_top():
            new_shape.append(PythonValue(ldim))
        elif ldim.val == 1:
            new_shape.append(PythonValue(rdim))
        elif rdim.val == 1:
            new_shape.append(PythonValue(ldim))
        else:
            TypeCheckLogger().new_warning(
                "W502",
                "ValueError: operands could not be broadcast together with shapes"
                f" {left.abstract_repr} {right.abstract_repr}",
                pos
            )
            return None

    return Tuple(new_shape)


# TODO(helq): Should generate warning to the user in case the array is not made of
# floats, for example np.array([[2,3], [6]]) has shape (2,) and its dtype is object :S
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


def array_from_AbstractValue(absval: AbstractValue, pos: Optional[Pos]) -> 'Optional[NdArray]':
    """Takes any AbstractValue and tries to convert it into a NdArray.

    Returns either a NdArray or None"""
    shape = getshape(absval)

    if shape is None:
        return None
    return NdArray(shape, pos)


def _function_array(val: PythonValue, pos: Optional[Pos]) -> PythonValue:
    """Takes any PythonValue and tries to convert it into a wrapped NdArray.

    Returns either a PythonValue(NdArray(...)) or a pv.Top"""
    if val.is_top():
        return PythonValue.top()

    absval = val.val
    assert isinstance(absval, AbstractValue)

    arr = array_from_AbstractValue(absval, pos)

    if arr is None:
        return PythonValue.top()
    return PythonValue(arr)


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
arange = BuiltinFun(
    'arange', _function_zero, args=[Int],
)

numpy_module = PythonValue(BuiltinModule(
    'numpy', {
        'ndarray': ndarray,
        'array': array,
        'zeros': zeros,
        'ones': ones,
        'arange': arange,
    }
))
