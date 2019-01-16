from enum import Enum
from functools import partial
from typing import Union, Optional, Any, TYPE_CHECKING

from .builtin_values import Int, Float, Bool, NoneType, ops_symbols
from .abstract_value import AbstractValue
from ..abstract_domain import AbstractDomain
from ..errors import TypeCheckLogger
from .objects_ids import new_id

from ..miscelaneous import Pos


if TYPE_CHECKING:
    from typing import Callable, Tuple, Dict, List as List_, Set, Type  # noqa: F401

    b_int = __builtins__.int
    b_bool = __builtins__.bool
    b_float = __builtins__.float


__all__ = ['PythonValue', 'PT', 'AbstractMutVal', 'List', 'int', 'float', 'bool', 'none', 'list']


class PT(Enum):
    """Python types supported in pytropos"""
    # Undefined = 0
    Top = 1
    # Bottom = 2
    InConstruction = 11


class PythonValue(AbstractDomain):
    def __init__(self,
                 val: Union[AbstractValue, PT] = PT.Top
                 ) -> None:
        self.val = val

    __top = None  # type: PythonValue

    @classmethod
    def top(cls) -> 'PythonValue':
        """Returns the Top element from the lattice: Any?"""
        if cls.__top is None:
            cls.__top = PythonValue(PT.Top)
        return cls.__top

    def is_top(self) -> 'b_bool':
        """Returns True if this object is the top of the lattice, ie, if Any?"""
        return self.val is PT.Top

    def join(self, other: 'PythonValue') -> 'PythonValue':
        if self.val is PT.Top or other.val is PT.Top:
            return PythonValue.top()

        assert isinstance(self.val, AbstractValue)
        assert isinstance(other.val, AbstractValue)

        if type(self.val) is type(other.val):  # noqa: E721
            return PythonValue(self.val.join(other.val))
        return PythonValue.top()

    def widen_op(self, other: 'PythonValue') -> 'Tuple[PythonValue, b_bool]':
        # eg: PythonValue(Int(5)) == PythonValue(Int(5))
        if self == other:
            return self, True

        # eg: PythonValue(PT.Top) and PythonValue(Int(5))
        if self.val is PT.Top or other.val is PT.Top:
            return PythonValue.top(), False

        # eg: PythonValue(Float(3)) and PythonValue(Int(5))
        if type(self.val) is not type(other.val):  # noqa: E721
            return PythonValue.top(), False

        assert isinstance(self.val, AbstractValue)
        assert isinstance(other.val, AbstractValue)

        # eg: PythonValue(List_([3])) and PythonValue(List_([3,5]))
        if self.__op_in_abstractvalue_overwritten(self.val.widen_op):
            new_val, fix = self.val.widen_op(other.val)
        # eg: PythonValue(Int(3)) and PythonValue(Int(5))
        else:
            new_val = self.val.join(other.val)
            # TODO(helq): This is not how a widening operator is defined, actually we
            # compare with <= not == !!!
            fix = new_val == self.val
        return PythonValue(new_val), fix

    def is_mut(self) -> 'b_bool':
        """Checks if the object is mutable"""
        return isinstance(self.val, AbstractMutVal)

    @property
    def mut_id(self) -> 'b_int':
        """Returns id of object if it is mutable"""
        assert isinstance(self.val, AbstractMutVal)
        return self.val.mut_id

    def copy_mut(self,
                 mut_heap: 'Dict[b_int, PythonValue]'
                 ) -> 'PythonValue':
        """Copies a mutable object recursively"""
        assert isinstance(self.val, AbstractMutVal)

        if self.mut_id in mut_heap:
            return mut_heap[self.mut_id]
        else:
            new_obj = mut_heap[self.mut_id] = PythonValue(PT.InConstruction)

            children = dict(self.val.children)
            for k, v in children.items():
                if v.is_mut():
                    children[k] = v.copy_mut(mut_heap)
            cls = type(self.val)
            new_obj.val = cls(children=children)

            return new_obj

    def convert_into_top(
            self,
            mut_heap: 'Dict[Tuple[str, b_int], Tuple[b_int, b_int, PythonValue]]',
            side: str
    ) -> None:
        """Makes a mutable object Top"""
        assert isinstance(self.val, AbstractMutVal)
        obj_iden = (side, self.mut_id)
        val_children = self.val.children

        self_topped = False
        if obj_iden in mut_heap:
            new_val = mut_heap[obj_iden][2]
            if not new_val.is_top():
                new_val.val = PT.Top
                self_topped = True
        else:
            mut_heap[obj_iden] = (self.mut_id, -1, PythonValue.top())
            self_topped = True

        if self_topped:
            children = dict(val_children)
            for k, v in children.items():
                if v.is_mut():
                    v.convert_into_top(mut_heap, side)

    def join_mut(self,  # noqa: C901
                 other: 'PythonValue',
                 mut_heap: 'Dict[Tuple[str, b_int], Tuple[b_int, b_int, PythonValue]]'
                 ) -> 'PythonValue':
        """Joining two mutable PythonValues"""
        assert isinstance(self.val, AbstractMutVal)
        assert isinstance(other.val, AbstractMutVal)

        left_iden = ('left', self.mut_id)
        right_iden = ('right', other.mut_id)

        # Checking if we have encounter already this value
        if (left_iden in mut_heap) or (right_iden in mut_heap):
            # self and other have already been joined
            if (left_iden in mut_heap) and mut_heap[left_iden][1] == other.mut_id:
                # assert right_iden in mut_heap
                assert mut_heap[right_iden][0] == self.mut_id
                return mut_heap[left_iden][2]

            # left has been already been joined with other object
            else:
                self.convert_into_top(mut_heap, 'left')
                other.convert_into_top(mut_heap, 'right')
                return PythonValue.top()

        if type(self.val) is not type(other.val):  # noqa: E721
            self.convert_into_top(mut_heap, 'left')
            other.convert_into_top(mut_heap, 'right')
            return PythonValue.top()

        new_obj = PythonValue(PT.InConstruction)
        mut_heap[left_iden] = mut_heap[right_iden] = \
            (self.mut_id, other.mut_id, new_obj)

        left_children = self.val.children
        right_children = other.val.children

        new_children = {}  # Dict[Any, PythonValue]

        # almost same code as found in store join
        for k in set(left_children).union(right_children):
            # The key is only in the left children
            if k not in right_children:
                # handling the mutable case
                left_val = left_children[k]
                if left_val.is_mut():
                    left_val.convert_into_top(mut_heap, "left")

                new_children[k] = PythonValue.top()

            # The key is only in the right store
            elif k not in left_children:
                # handling the mutable case
                right_val = right_children[k]
                if right_val.is_mut():
                    right_val.convert_into_top(mut_heap, "right")

                new_children[k] = PythonValue.top()

            # the key is only in right children
            else:
                val1 = left_children[k]
                val2 = right_children[k]

                if val1.is_mut():
                    if val2.is_mut():  # both (val1 and val2) are mutable
                        new_children[k] = val1.join_mut(val2, mut_heap)

                    else:  # val1 mutable, val2 not mutable
                        val1.convert_into_top(mut_heap, 'left')
                        new_children[k] = PythonValue.top()

                else:
                    if val2.is_mut():  # val1 not mutable, val2 mutable
                        val2.convert_into_top(mut_heap, 'right')
                        new_children[k] = PythonValue.top()

                    else:  # both (val1 and val2) are not mutable
                        new_children[k] = val1.join(val2)

        cls = type(self.val)
        new_obj.val = cls(children=new_children)

        return new_obj

    def __eq__(self, other: Any) -> 'b_bool':
        if self is other:
            return True
        if not isinstance(other, PythonValue):
            return False
        return self.val == other.val

    __repr_visited = set()  # type: Set[b_int]

    def __repr__(self) -> str:
        if self.val is PT.Top:
            return "Top"
        # elif self.val is PT.Undefined:
            # return "Undefined"
        else:  # self.type is PT.Top
            assert not isinstance(self.val, PT)
            if self.is_mut():
                if self.mut_id in self.__repr_visited:
                    return 'Ref'
                else:
                    self.__repr_visited.add(self.mut_id)
                    r = self.val.abstract_repr
                    self.__repr_visited.remove(self.mut_id)
                    return r
            else:
                return self.val.abstract_repr

    def __getattr__(self, name: str) -> Any:
        # Checking if name is add, mul, truediv
        if name in ops_symbols.keys():
            return partial(self.operate, name)
        raise AttributeError(f"There is no operation for PythonValues called '{name}'")

    @staticmethod
    def __op_in_abstractvalue_overwritten(method: Any) -> 'b_bool':
        """Checks whether the method (defined in AbstractValue) was overwriten or not"""
        notoverwritten = hasattr(method, '__qualname__') and \
            method.__qualname__.split('.')[0] == "AbstractValue"
        return not notoverwritten  # ie, True if method overwritten

    def operate(self, op: str, other: 'PythonValue', pos: Optional[Pos] = None) -> 'PythonValue':
        op_sym = ops_symbols[op]

        if self.val is PT.Top or other.val is PT.Top:
            return PythonValue.top()

        # This assert is always true, it's just to keep Mypy from crying
        assert isinstance(self.val, AbstractValue), \
            f"Left type is {type(self.val)} but should have been an AbstractValue"
        assert isinstance(other.val, AbstractValue), \
            f"Left type is {type(other.val)} but should have been an AbstractValue"

        # If both values have the same type use val.op_add(otherval)
        if type(self.val) is type(other.val):  # noqa: E721
            # Checking if op_add has been overwritten by the class that has been called
            # If it hasn't, the operation result is Top
            op_method = getattr(self.val, f'op_{op}')
            if self.__op_in_abstractvalue_overwritten(op_method):
                newval = op_method(other.val, pos)
            else:
                TypeCheckLogger().new_warning(
                    "E009",
                    f"TypeError: unsupported operand type(s) for {op_sym}: "
                    f"'{self.val.type_name}' and '{other.val.type_name}'",
                    pos)

                newval = PT.Top

        # If values have different type use val.op_add_OtherType(otherval)
        # or otherval.op_add_Type(val)
        else:
            leftOpName = "op_r{op}_{class_name}".format(op=op, class_name=type(self.val).__name__)
            rightOpName = "op_{op}_{class_name}".format(op=op, class_name=type(other.val).__name__)

            try:
                newval = getattr(self.val, rightOpName)(other.val, pos)
            except:  # noqa: E772
                try:
                    newval = getattr(other.val, leftOpName)(self.val, pos)
                except:  # noqa: E772
                    TypeCheckLogger().new_warning(
                        "E009",
                        f"TypeError: unsupported operand type(s) for {op_sym}: "
                        f"'{self.val.type_name}' and '{other.val.type_name}'",
                        pos)

                    newval = PT.Top

        if newval is None:
            return PythonValue.top()
        return PythonValue(newval)

    def bool(self, pos: Optional[Pos] = None) -> 'PythonValue':
        """method documentation"""
        if isinstance(self.val, Bool):
            return self

        if self.val is PT.Top:
            return PythonValue(Bool.top())

        assert isinstance(self.val, AbstractValue)

        op_method = self.val.op_bool
        if self.__op_in_abstractvalue_overwritten(op_method):
            bool_val = op_method(pos)

            # Checking bool_val is a boolean!
            if not isinstance(bool_val, Bool):
                TypeCheckLogger().new_warning(
                    "E010",
                    f"TypeError: __bool__ should return bool, returned {bool_val.val.type_name}",
                    pos)
                return PythonValue(Bool.top())

            return PythonValue(bool_val)

        # TODO(helq): If the operation was not defined more stuff is to be done, like
        # checking __len__.
        # More info: https://docs.python.org/3/reference/datamodel.html#object.__bool__
        return PythonValue(Bool.top())


class AbstractMutVal(AbstractValue):
    """An AbstractValue that allows mutability"""

    def __init__(self, children: 'Optional[Dict[Any, PythonValue]]' = None) -> None:
        """Init must always be called

        All attributes and values must be stored into `children`"""
        self.__mut_id = new_id()  # type: b_int
        self.children = {} if children is None else children

    @property
    def mut_id(self) -> 'b_int':
        """Unique id of object"""
        return self.__mut_id

    def join(self, other: 'Any') -> 'Any':
        """Join should never be called.

        It is strange to have an AbstractValue (AbstractDomain) which doesn't not define a
        `join` operation. The reason is that this class is very tightly coupled to
        PythonValue. PythonValue is who actually implements the functionality of joining
        AbstractMutVals"""
        raise NotImplementedError()


class List(AbstractMutVal):
    def __init__(self,
                 lst: 'Optional[List_[PythonValue]]' = None,
                 children: 'Optional[Dict[Any, PythonValue]]' = None
                 ) -> None:
        super().__init__(children)

        if lst is not None:
            assert children is None, "Cannot initialise List with both a list and children"
            # Copying list to children values
            for i, val in enumerate(lst):
                self.children[('index', i)] = val
            self.children['size'] = int(len(lst))

        elif children is None:  # lst is None, and children is {}
            self.__im_top = True
            return

        self.__im_top = False

    def __eq__(self, other: Any) -> 'b_bool':
        raise NotImplementedError()

    @property
    def abstract_repr(self) -> 'str':
        if self.is_top():
            return 'list?'

        size = self.children['size']
        assert isinstance(size.val, Int)
        if size.val.val == 0:
            return '[]'

        indices: 'List_[Tuple[b_int, PythonValue]]'
        indices = sorted([(i[1], v) for i, v in self.children.items() if isinstance(i, tuple)])
        # print(f"indices = {indices}")

        output = []  # type: List_[str]
        i = 0
        for j, v in indices:
            if i == j:
                i += 1
            else:
                i = j
                output.append(f"...")
            output.append(repr(v))

        if size.val.is_top():
            output.append('...')

        return 'List([' + ', '.join(output) + f'], size={size})'

    __top = None  # type: List

    @classmethod
    def top(cls) -> 'List':
        if cls.__top is None:
            cls.__top = List()
        return cls.__top

    def is_top(self) -> 'b_bool':
        return self.__im_top

    @property
    def type_name(self) -> str:
        return "list"


def int(val: 'Optional[b_int]' = None) -> PythonValue:
    """Returns an Int wrapped into a PythonValue"""
    return PythonValue(Int(val))


def float(val: 'Optional[b_float]' = None) -> PythonValue:
    """Returns a Float wrapped into a PythonValue"""
    # assert val is None or isinstance(val, __builtins__['float']), \
    #     f"I accept either a float or a None value, but I was given {type(val)}"
    return PythonValue(Float(val))


def bool(val: 'Optional[b_bool]' = None) -> PythonValue:
    """Returns a Bool wrapped into a PythonValue"""
    return PythonValue(Bool(val))


def __createNonePV() -> Any:
    """Building a single wrapped value for NoneType

    Why waste memory on a class that contains a unique element.

    Creating an element of type NoneType and returning it every single time.

    :return: a NoneType wrapped into a PythonValue
    """
    none = PythonValue(NoneType())

    def retNone() -> PythonValue:
        nonlocal none
        return none
    return retNone


none = __createNonePV()  # type: Callable[[], PythonValue]


def list(lst: 'Optional[List_[PythonValue]]' = None) -> PythonValue:
    """Returns a Bool wrapped into a PythonValue"""
    return PythonValue(List(lst=lst))


if __name__ == '__main__':
    val1 = PythonValue.top()
    val2 = int()
    val3 = int(2)
    val4 = int(3)
    print(f"{val1} + {val2} == {val1.add(val2)}")
    print(f"{val1} + {val3} == {val1.add(val3)}")
    print(f"{val2} + {val3} == {val2.add(val3)}")
    print(f"{val3} + {val4} == {val3.add(val4)}")
    print(f"{val3} * {val4} == {val3.mul(val4)}")

    val2 = float()
    val3 = float(0.0)
    val4 = float(3.0)
    val5 = val3.floordiv(val3)
    print(f"{val1} + {val2} == {val1.add(val2)}")
    print(f"{val1} + {val3} == {val1.add(val3)}")
    print(f"{val2} + {val3} == {val2.add(val3)}")
    print(f"{val3} + {val4} == {val3.add(val4)}")
    print(f"{val3} * {val4} == {val3.mul(val4)}")
    print(f"{val3} / {val3} == {val3.truediv(val3)}")
    print(f"{val3} // {val3} == {val5}")
    print(f"{val5}.is_top() == {val5.is_top()}")

    val1 = int(0)
    val2 = float(1.0)
    print(f"{val1} / {val2} == {val1.truediv(val2)}")

    val1 = bool(True)
    val2 = int()
    print(f"{val1} + {val2} == {val1.add(val2)}")

    val1 = bool(True)
    val2 = bool(True)
    print(f"{val1} + {val2} == {val1.add(val2)}")

    val1 = bool(True)
    val2 = int()
    print(f"{val1} << {val2} == {val1.lshift(val2)}")

    val1 = none()
    val2 = int(3)
    print(f"{val1} << {val2} == {val1.lshift(val2)}")

    print(f"NoneType() is NoneType() == {NoneType() is NoneType()}")
    print(f"none() is none() == {none() is none()}")

    print(f"Errors: {TypeCheckLogger()}")

    # Using List as arbitrary python objects
    # val1 = PythonValue(List(children={'size': int(2)}))
    # val2 = PythonValue(List(children={'size': int(3)}))

    # print(val1)
    # print(val2)

    # val3 = val1.join_mut(val2, {})

    # print(val3)
    # print()

    # # What if we add recursion?
    # val1 = PythonValue(List(children={'size': int(3)}))
    # val2 = PythonValue(List(children={'size': int(2)}))

    # val1.val.children['me'] = val1  # type: ignore
    # val2.val.children['me'] = val2  # type: ignore

    # print(val1)
    # print(val2)

    # val3 = val1.join_mut(val2, {})

    # print(val3)
    # print()

    # Using other lists
    val1 = list([int(3), float(3.0)])
    val2 = list([int(5)])

    val2.val.children[('index', 1)] = val2  # type: ignore
    val2.val.children['size'] = int(2)  # type: ignore

    print(val1)
    print(val2)

    val3 = val1.join_mut(val2, {})

    print(val3)
