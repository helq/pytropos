import math
import re
from typing import Dict, Optional, Any, Tuple as Tuple_, Union
from typing import List as List_  # noqa: F401

from ..internals.values.python_values.python_values import (
    AbstractMutVal, PT, PythonValue, AttrsContainer, AttrsMutContainer,
    AttrsTopContainer, SubscriptsContainer
)
from ..internals.values.abstract_value import AbstractValue
from ..internals.values.builtin_values import Int
import pytropos.internals.values as pv
from ..internals.values.python_values.builtin_mutvalues import Tuple, List
from ..internals.values.python_values.wrappers import (
    BuiltinClass, BuiltinModule, BuiltinFun, BuiltinType
)
from ..internals.errors import TypeCheckLogger

from ..internals.miscelaneous import Pos


__all__ = [
    'NdArray', 'ndarray', 'array', 'zeros', 'ones', 'arange', 'numpy_module',
    'check_numpy_module', 'NdArrayAnnotation'
]


extract_op = re.compile(r'op_([a-zA-Z]*)(_([a-zA-Z]*))?$')


class NdArrayAnnotation(BuiltinType):
    def __init__(  # noqa: C901
            self,
            array: 'Optional[NdArray]' = None,
            children: 'Optional[Dict[Any, PythonValue]]' = None
    ) -> None:
        super().__init__(children=children)

        if array is not None:
            self.children['array'] = PythonValue(array)
        elif children is None:
            self._im_top = True
            return

        self._im_top = False

    @property
    def abstract_repr(self) -> str:
        if self.is_top():
            return 'NdArray'

        array = self.children['array'].val
        assert isinstance(array, NdArray)
        if array.is_top():
            return 'NdArray'

        shape = array.children['shape'].val
        assert isinstance(shape, Tuple)

        return f"NdArray[{','.join(shape._elems())}]"

    @property
    def type_name(self) -> str:
        return '<type/class NdArrayAnnotation>'

    @classmethod
    def top(cls) -> 'NdArrayAnnotation':
        return NdArrayAnnotation()

    def is_top(self) -> 'bool':
        return self._im_top

    def copy_mut(self,
                 mut_heap: 'Dict[int, PythonValue]'
                 ) -> 'NdArrayAnnotation':
        if self.is_top():
            return self
        toret = super().copy_mut(mut_heap)
        toret._im_top = False
        return toret  # type: ignore

    def join_mut(self,
                 other: 'NdArrayAnnotation',
                 mut_heap: 'Dict[Tuple_[str, int], Tuple_[int, int, PythonValue]]',
                 ) -> 'NdArrayAnnotation':
        assert type(self) is type(other)
        new = super().join_mut(other, mut_heap)
        if self.is_top() or other.is_top():
            return self.top()
        new._im_top = False
        return new  # type: ignore

    def get_subscripts(self, pos: 'Optional[Pos]') -> SubscriptsContainer:
        return SubscriptsNdArrayAnnContainer(pos)

    def get_absvalue(self) -> 'PythonValue':
        if self.is_top():
            return PythonValue(NdArray.top())
        return self.children['array']

    def get_attrs(self) -> 'AttrsContainer':
        # TODO(helq): show error message, similar to how list does it
        return AttrsTopContainer()


class SubscriptsNdArrayAnnContainer(SubscriptsContainer):
    def __init__(self, pos: 'Optional[Pos]') -> None:
        self.pos = pos

    def __getitem__(self, key: PythonValue) -> PythonValue:
        if key.is_top():
            return PythonValue(NdArrayAnnotation())

        absval = key.val
        if isinstance(absval, Int):
            return PythonValue(NdArrayAnnotation(NdArray(key)))
        if isinstance(absval, BuiltinType):
            key = absval.get_absvalue()
            if isinstance(key.val, Int):
                return PythonValue(NdArrayAnnotation(NdArray(key)))
        elif isinstance(absval, Tuple):
            shape = absval.copy_mut({})
            for k, v in shape.children.items():
                if isinstance(v.val, BuiltinType):
                    shape.children[k] = v.val.get_absvalue()
            return PythonValue(NdArrayAnnotation(NdArray(shape)))

        return PythonValue(NdArrayAnnotation())

    # TODO(helq): throw warning if something weird is trying to be done
    def __delitem__(self, key: PythonValue) -> None:
        pass

    def __setitem__(self, key_: PythonValue, val: PythonValue) -> None:
        pass


class NdArray(AbstractMutVal):
    def __init__(  # noqa: C901
            self,
            shape: 'Union[PythonValue, Tuple, None]' = None,
            pos: 'Optional[Pos]' = None,
            children: 'Optional[Dict[Any, PythonValue]]' = None
    ) -> None:
        super().__init__(children=children)
        if shape is not None:
            assert children is None
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
                shape.val = self._check_tuple_all_ints(shape.val, pos)

            elif isinstance(shape, Tuple):
                shape = self._check_tuple_all_ints(shape, pos)
                shape = PythonValue(shape)
            else:  # shape.is_top()
                self._im_top = True
                return

            self.children['shape'] = shape

            self.children[('attr', 'dot')] = \
                PythonValue(BuiltinFun(
                    'dot',
                    NdArray._method_dot,
                    self,
                    args=[AbstractValue]
                ))

        elif children is None:  # shape is None and children is None
            self._im_top = True
            return

        self._im_top = False

    def _check_tuple_all_ints(self, shape: Tuple, pos: 'Optional[Pos]') -> Tuple:
        shape = shape.copy_mut({})
        for k in shape.children:
            if isinstance(k, tuple) and k[0] == 'index':
                value = shape.children[k]

                if value.is_top():
                    shape.children[k] = PythonValue(Int.top())
                elif not isinstance(value.val, Int):
                    assert isinstance(value.val, AbstractValue)
                    TypeCheckLogger().new_warning(
                        "E017",
                        f"TypeError: '{value.val.type_name}' object cannot"
                        " be interpreted as an integer",
                        pos)
                    shape.children[k] = pv.int()
        return shape

    def __repr__(self) -> str:
        if self.is_top():
            return "NdArray()?"
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
        # if self.is_top() or other.is_top():
        #     return self.top()
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
        if not hasattr(self, '_attrs'):
            self._attrs = AttrsMutContainer(
                'ndarray',
                self.children,
                {
                    'shape': self._attr_shape,
                    'ndim': self._attr_ndim,
                },
                read_only=True
            )
        return self._attrs

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
            if op[3] is None:  # ex: op_add
                return object.__getattribute__(self, 'op_OP')
            else:  # ex: op_add_Int
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
        if self.is_top():
            return PythonValue(Tuple.top())

        assert isinstance(self.children['shape'].val, Tuple)
        return self.children['shape'].copy_mut({})

    def _attr_ndim(self) -> 'PythonValue':
        if self.is_top():
            return PythonValue(Int.top())

        shape = self.children['shape'].val
        assert isinstance(shape, Tuple)

        if shape.is_size_determined():
            return PythonValue(Int(shape.size[0]))
        else:
            return PythonValue(Int.top())

    def _method_dot(self, other: 'PythonValue', pos: Optional[Pos]) -> 'PythonValue':  # noqa: C901
        """Checking done with the same rules defined in numpy documentation.

        doc url: https://docs.scipy.org/doc/numpy/reference/generated/numpy.dot.html"""
        if self.is_top() or other.is_top():
            return PythonValue.top()

        other_array = _function_array(other, pos)
        if other_array.is_top():
            new_array = self.top()
        else:
            assert isinstance(other_array.val, NdArray)
            self_shape = self.shape
            other_shape = other_array.val.shape
            if not self_shape.is_size_determined() or not other_shape.is_size_determined():
                new_array = self.top()
            else:
                self_size = self_shape.size[0]
                other_size = other_shape.size[0]

                # Both arrays are 1-D
                if self_size == 1 and other_size == 1:
                    self_indices = self_shape.sorted_indices_ints()
                    other_indices = other_shape.sorted_indices_ints()
                    s_index0 = self_indices[0]
                    o_index0 = other_indices[0]

                    if s_index0.is_top() or o_index0.is_top():
                        new_array = self.top()
                    elif s_index0 == o_index0:
                        new_array = NdArray(Tuple([]))
                    else:
                        new_array = self.top()
                        TypeCheckLogger().new_warning(
                            "W503",
                            f"ValueError: shapes {self_shape.abstract_repr} "
                            f"and {other_shape.abstract_repr} not aligned: "
                            f"{s_index0.abstract_repr} (dim 0)"
                            f" != {o_index0.abstract_repr} (dim 0)",
                            pos
                        )

                # Both arrays are 2-D
                elif self_size == other_size == 2:
                    self_indices = self_shape.sorted_indices_ints()
                    other_indices = other_shape.sorted_indices_ints()
                    s_index1 = self_indices[1]
                    o_index0 = other_indices[0]
                    if s_index1.is_top() or o_index0.is_top():
                        new_array = self.top()
                    elif s_index1 == o_index0:
                        new_array = NdArray(Tuple([PythonValue(self_indices[0]),
                                                   PythonValue(other_indices[1])]))
                    else:
                        new_array = self.top()
                        TypeCheckLogger().new_warning(
                            "W503",
                            f"ValueError: shapes {self_shape.abstract_repr} "
                            f"and {other_shape.abstract_repr} not aligned: "
                            f"{s_index1.abstract_repr} (dim 1)"
                            f" != {o_index0.abstract_repr} (dim 0)",
                            pos
                        )

                # Either array is 0-D
                elif self_size == 0:
                    new_array = NdArray(other_shape)
                elif other_size == 0:
                    new_array = NdArray(self_shape)

                # Other array is 1-D
                elif other_size == 1:
                    self_indices = self_shape.sorted_indices_ints()
                    other_indices = other_shape.sorted_indices_ints()
                    s_index_last = self_indices[-1]
                    o_index0 = other_indices[0]

                    if s_index_last.is_top() or o_index0.is_top():
                        new_array = self.top()
                    elif s_index_last == o_index0:
                        new_array = NdArray(Tuple([PythonValue(idx) for idx in self_indices[:-1]]))
                    else:
                        new_array = self.top()
                        TypeCheckLogger().new_warning(
                            "W503",
                            f"ValueError: shapes {self_shape.abstract_repr} "
                            f"and {other_shape.abstract_repr} not aligned: "
                            f"{s_index_last.abstract_repr} (dim {self_size-1})"
                            f" != {o_index0.abstract_repr} (dim 0)",
                            pos
                        )

                # Both arrays are arbritrary dimentioned matrices
                else:
                    self_indices = self_shape.sorted_indices_ints()
                    other_indices = other_shape.sorted_indices_ints()
                    s_index_last = self_indices[-1]
                    o_index_2d_last = other_indices[-2]

                    if s_index_last.is_top() or o_index_2d_last.is_top():
                        new_array = self.top()
                    elif s_index_last == o_index_2d_last:
                        new_indices = self_indices[:-1]
                        new_indices.extend(other_indices[:-2])
                        new_indices.append(other_indices[-1])

                        new_array = NdArray(Tuple([PythonValue(idx) for idx in new_indices]))
                    else:
                        new_array = self.top()
                        TypeCheckLogger().new_warning(
                            "W503",
                            f"ValueError: shapes {self_shape.abstract_repr} "
                            f"and {other_shape.abstract_repr} not aligned: "
                            f"{s_index_last.abstract_repr} (dim {self_size-1})"
                            f" != {o_index_2d_last.abstract_repr} (dim {other_size-2})",
                            pos
                        )
        return PythonValue(new_array)


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
                assert isinstance(shape_val, Tuple)
                pv = PythonValue(PT.InConstruction)
                sh_id, sh_ot_id = shape_val.mut_id, shape_val_other.mut_id
                mut_heap = {
                    ('left',     sh_id): (sh_id, sh_ot_id, pv),
                    ('right', sh_ot_id): (sh_id, sh_ot_id, pv)
                }
                shape_val = shape_val.join_mut(shape_val_other, mut_heap)

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


def _function_zeros(val: PythonValue, pos: Optional[Pos]) -> PythonValue:
    return PythonValue(NdArray(val, pos))


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
    'zeros', _function_zeros, args=[(Tuple, Int, List)],
)
ones = BuiltinFun(
    'ones', _function_zeros, args=[(Tuple, Int, List)],
)
arange = BuiltinFun(
    'arange', _function_zeros, args=[Int],
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

check_numpy_module = PythonValue(BuiltinModule(
    'pytropos.check.numpy', {
        'NdArray': NdArrayAnnotation()
    }
))
