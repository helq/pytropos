from abc import ABC, abstractmethod
from enum import Enum
from functools import partial
# from math import isinf
from typing import Union, Optional, Any
from typing import Callable, Tuple, Dict, List, Set, Type  # noqa: F401

from ..builtin_values import Bool, ops_symbols
from ..abstract_value import AbstractValue
from ...abstract_domain import AbstractDomain
from ...errors import TypeCheckLogger
from .objects_ids import new_id

from ...miscelaneous import Pos


__all__ = ['PythonValue', 'PT', 'AbstractMutVal', 'Args']


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

    def is_top(self) -> 'bool':
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

    def widen_op(self, other: 'PythonValue') -> 'Tuple[PythonValue, bool]':
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

        # eg: PythonValue(List([3])) and PythonValue(List([3,5]))
        if self.__op_in_abstractvalue_overwritten(self.val.widen_op):
            new_val, fix = self.val.widen_op(other.val)
        # eg: PythonValue(Int(3)) and PythonValue(Int(5))
        else:
            new_val = self.val.join(other.val)
            # TODO(helq): This is not how a widening operator is defined, actually we
            # compare with <= not == !!!
            fix = new_val == self.val
        return PythonValue(new_val), fix

    def is_mut(self) -> 'bool':
        """Checks if the object is mutable"""
        return isinstance(self.val, AbstractMutVal)

    @property
    def mut_id(self) -> 'int':
        """Returns id of object if it is mutable"""
        assert isinstance(self.val, AbstractMutVal)
        return self.val.mut_id

    def copy_mut(self,
                 mut_heap: 'Dict[int, PythonValue]'
                 ) -> 'PythonValue':
        """Copies a mutable object recursively"""
        assert isinstance(self.val, AbstractMutVal)
        if self.is_top():
            return self

        if self.mut_id in mut_heap:
            return mut_heap[self.mut_id]
        else:
            new_obj = mut_heap[self.mut_id] = PythonValue(PT.InConstruction)
            new_obj.val = self.val.copy_mut(mut_heap)
            return new_obj

    def convert_into_top(self, converted: 'Set[int]') -> None:
        """Makes the underlying AbstractMutVal Top"""
        assert isinstance(self.val, AbstractMutVal)
        self.val.convert_into_top(converted)
        self.val = self.val.top()

    def new_vals_to_top(
            self,
            mut_heap: 'Dict[Tuple[str, int], Tuple[int, int, PythonValue]]',
            side: str
    ) -> None:
        """Makes a mutable object Top"""
        assert isinstance(self.val, AbstractMutVal)
        self.val.new_vals_to_top(mut_heap, side)

    def join_mut(self,
                 other: 'PythonValue',
                 mut_heap: 'Dict[Tuple[str, int], Tuple[int, int, PythonValue]]'
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
                assert mut_heap[right_iden][2] is mut_heap[left_iden][2]
                return mut_heap[left_iden][2]

            # left has been already been joined with other object
            else:
                self.new_vals_to_top(mut_heap, 'left')
                other.new_vals_to_top(mut_heap, 'right')
                return PythonValue.top()

        if type(self.val) is not type(other.val):  # noqa: E721
            self.new_vals_to_top(mut_heap, 'left')
            other.new_vals_to_top(mut_heap, 'right')
            return PythonValue.top()

        # If the value is top the result its top
        if self.val.is_top():
            other.new_vals_to_top(mut_heap, 'right')
            return PythonValue(self.val.top())
        if other.val.is_top():
            self.new_vals_to_top(mut_heap, 'right')
            return PythonValue(self.val.top())

        new_obj = PythonValue(PT.InConstruction)
        mut_heap[left_iden] = mut_heap[right_iden] = \
            (self.mut_id, other.mut_id, new_obj)

        new_val = self.val.join_mut(other.val, mut_heap)
        if new_obj.val == PT.InConstruction:
            new_obj.val = new_val
        # Notice that we don't change the value of the Object if it is not InConstruction.
        # If a PythonValue is not anymore in construction it means that it has been made
        # "top" by some call before it

        return new_obj

    # TODO(helq): This equality function is faulty (because of the underlying mutable
    # variables). An equality function should be defined in Store, not here, to compare
    # two different Stores. Similar to how `join_mut` is defined
    def __eq__(self, other: Any) -> 'bool':
        if self is other:
            return True
        if not isinstance(other, PythonValue):
            return False
        return self.val == other.val

    __repr_visited = set()  # type: Set[int]

    def __repr__(self) -> str:
        if self.val is PT.Top:
            return "Top"
        elif self.val is PT.InConstruction:
            return "InConstruction"
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

    # TODO(helq): Improve by checking if the given parameters correspond to the arguments
    # the function receives, if not return Top
    def call(self,
             store: Any,
             args: 'Args',
             pos: Optional[Pos] = None) -> 'PythonValue':
        if self.is_top():
            return PythonValue.top()

        # This assert is always true, it's just to keep Mypy from crying
        assert isinstance(self.val, AbstractValue), \
            f"The type is {type(self.val)} but should have been an AbstractValue"

        call_method = self.val.fun_call
        if self.__op_in_abstractvalue_overwritten(call_method):
            newval = call_method(store, args, pos)  # type: PythonValue
            assert isinstance(newval, PythonValue), "A function call didn't return a PythonValue"
        else:
            TypeCheckLogger().new_warning(
                "E016",
                f"TypeError: '{self.val.type_name}' object is not callable",
                pos)

            newval = PythonValue.top()

        return newval

    @property
    def attr(self) -> 'AttrsContainer':
        if self.is_top():
            return AttrsTopContainer()

        # This assert is always true, it's just to keep Mypy from crying
        assert isinstance(self.val, AbstractValue), \
            f"The type is {type(self.val)} but should have been an AbstractValue"

        call_method = self.val.get_attrs
        if self.__op_in_abstractvalue_overwritten(call_method):
            return call_method()  # type: ignore
        else:
            return AttrsTopContainer()

    def subs(self, pos: 'Optional[Pos]' = None) -> 'SubscriptsContainer':
        if self.is_top():
            return SubscriptsTopContainer()

        # This assert is always true, it's just to keep Mypy from crying
        assert isinstance(self.val, AbstractValue), \
            f"The type is {type(self.val)} but should have been an AbstractValue"

        call_method = self.val.get_subscripts
        if self.__op_in_abstractvalue_overwritten(call_method):
            return call_method(pos)  # type: ignore
        else:
            TypeCheckLogger().new_warning(
                "E015",
                f"TypeError: '{self.val.type_name}' object is not subscriptable",
                pos)
            return SubscriptsTopContainer()

    def __getattr__(self, name: str) -> Any:
        # Checking if name is add, mul, truediv
        if name in ops_symbols.keys():
            return partial(self.operate, name)
        raise AttributeError(f"PythonValue has no attribute called '{name}'")

    @staticmethod
    def __op_in_abstractvalue_overwritten(method: Any) -> 'bool':
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
            except AttributeError:
                try:
                    newval = getattr(other.val, leftOpName)(self.val, pos)
                except AttributeError:
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

    def type(self) -> str:
        """Returns the type of the value hold self.val"""
        if self.val is PT.Top:
            return "Top"
        elif self.val is PT.InConstruction:
            return "InConstruction"
        else:  # self.type is PT.Top
            assert not isinstance(self.val, PT)
            return str(self.val.type_name)

    def __lt__(self, other: 'PythonValue') -> '__builtins__.bool':
        if self.is_top():
            return False
        elif other.is_top():
            return True

        assert isinstance(self.val, AbstractValue)
        assert isinstance(other.val, AbstractValue)

        if type(self.val) is not type(other.val):  # noqa: E721
            return False

        try:
            return bool(self.val < other.val)  # type: ignore
        except TypeError:
            # TODO(helq): Add warning saying that comparing this two elements is not fully
            # supported and may be very slow
            pass

        # Two know if a value in a Lattice is bigger than the other one can do:
        # join(self, other) == other
        if isinstance(self.val, AbstractMutVal):
            joining = self.join_mut(other, {}).val
        else:
            joining = self.val.join(other.val)

        return bool(joining == other.val)


class AbstractMutVal(AbstractValue):
    """An AbstractValue that allows mutability"""

    def __init__(self, children: 'Optional[Dict[Any, PythonValue]]' = None) -> None:
        """Init must always be called

        All attributes and values must be stored into `children`"""
        self.__mut_id = new_id()  # type: int
        self.children = {} if children is None else children

    @property
    def mut_id(self) -> 'int':
        """Unique id of object"""
        return self.__mut_id

    __eq_visited = ({}, {})  # type: Tuple[Dict[int, int], Dict[int, int]]

    def __eq__(self, other: Any) -> bool:
        if self is other:
            return True
        if not isinstance(other, AbstractMutVal):
            return False
        if self.mut_id in AbstractMutVal.__eq_visited[0]:
            return AbstractMutVal.__eq_visited[0][self.mut_id] == other.mut_id
        if other.mut_id in AbstractMutVal.__eq_visited[1]:
            return AbstractMutVal.__eq_visited[1][other.mut_id] == self.mut_id

        AbstractMutVal.__eq_visited[0][self.mut_id] = other.mut_id
        AbstractMutVal.__eq_visited[1][other.mut_id] = self.mut_id
        eq = self.children == other.children
        del AbstractMutVal.__eq_visited[0][self.mut_id]
        del AbstractMutVal.__eq_visited[1][other.mut_id]

        return eq

    def convert_into_top(self, converted: 'Set[int]') -> None:
        """Makes all children objects connected to this into Top"""
        if self.mut_id in converted:
            return

        converted.add(self.mut_id)

        children = self.children
        for k, v in children.items():
            if v.is_mut():
                assert isinstance(v.val, AbstractMutVal)
                v.convert_into_top(converted)
        children.clear()

    def new_vals_to_top(
            self,
            mut_heap: 'Dict[Tuple[str, int], Tuple[int, int, PythonValue]]',
            side: str
    ) -> None:
        """Makes all new children objects connected to this into Top"""
        obj_iden = (side, self.mut_id)
        val_children = self.children

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
                    assert isinstance(v.val, AbstractMutVal)
                    v.val.new_vals_to_top(mut_heap, side)

    def copy_mut(self, mut_heap: 'Dict[int, PythonValue]') -> 'Any':
        """Makes a copy of the current AbstractMutVal.

        It must be overwritten to add stuff that is not children (PythonValue's)"""
        if self.is_top():
            return self

        assert len(mut_heap) > 0 \
            and self.mut_id in mut_heap, \
            "copy_mut cannot be called with an empty mut_heap!"

        children = dict(self.children)
        for k, v in children.items():
            if v.is_mut():
                children[k] = v.copy_mut(mut_heap)
        cls = type(self)
        return cls(children=children)

    def join(self, other: 'Any') -> 'Any':
        """Join should never be called.

        It is strange to have an AbstractValue (AbstractDomain) which doesn't not define a
        `join` operation. The reason is that this class is very tightly coupled to
        PythonValue. PythonValue is who actually implements the functionality of joining
        AbstractMutVals"""
        raise NotImplementedError()

    # TODO(helq): any children that doesn't appear on both branches should produce a
    # warning
    def join_mut(self,
                 other: 'Any',
                 mut_heap: 'Dict[Tuple[str, int], Tuple[int, int, PythonValue]]',
                 ) -> 'Any':
        """Joins both values including their children"""
        assert not self.is_top() and not other.is_top()
        assert len(mut_heap) > 0 \
            and ('left', self.mut_id) in mut_heap \
            and ('right', other.mut_id) in mut_heap, \
            "join_mut cannot be called with an empty mut_heap!"

        left_children = self.children
        right_children = other.children

        new_children = {}  # Dict[Any, PythonValue]

        # almost same code as found in store join
        for k in set(left_children).union(right_children):
            # The key is only in the left children
            if k not in right_children:
                # handling the mutable case
                left_val = left_children[k]
                if left_val.is_mut():
                    left_val.new_vals_to_top(mut_heap, "left")

                new_children[k] = PythonValue.top()

            # The key is only in the right store
            elif k not in left_children:
                # handling the mutable case
                right_val = right_children[k]
                if right_val.is_mut():
                    right_val.new_vals_to_top(mut_heap, "right")

                new_children[k] = PythonValue.top()

            # the key is only in right children
            else:
                val1 = left_children[k]
                val2 = right_children[k]

                if val1.is_mut():
                    if val2.is_mut():  # both (val1 and val2) are mutable
                        new_children[k] = val1.join_mut(val2, mut_heap)

                    else:  # val1 mutable, val2 not mutable
                        val1.new_vals_to_top(mut_heap, 'left')
                        new_children[k] = PythonValue.top()

                else:
                    if val2.is_mut():  # val1 not mutable, val2 mutable
                        val2.new_vals_to_top(mut_heap, 'right')
                        new_children[k] = PythonValue.top()

                    else:  # both (val1 and val2) are not mutable
                        new_children[k] = val1.join(val2)

        cls = type(self)
        return cls(children=new_children)

    def get_attrs(self) -> 'AttrsContainer':
        if self.is_top():
            return AttrsTopContainer()
        return AttrsMutContainer(self.type_name, self.children)


class Args:
    def __init__(
            self,
            vals: 'Tuple[PythonValue, ...]',
            args: 'Optional[PythonValue]' = None,
            kargs: 'Optional[Dict[str, PythonValue]]' = None
    ) -> None:
        """Basic support for arguments to pass to a function"""
        self.vals = vals
        self.args = args
        self.kargs = kargs


class AttrsContainer(ABC):
    """This class acts as a Dict[str, PythonValue]"""
    @abstractmethod
    def __getitem__(self, key_: 'Union[str, Tuple[str, Pos]]') -> PythonValue:
        raise NotImplementedError()

    @abstractmethod
    def __delitem__(self, key_: 'Union[str, Tuple[str, Pos]]') -> None:
        raise NotImplementedError()

    @abstractmethod
    def __setitem__(self, key_: 'Union[str, Tuple[str, Pos]]', val: PythonValue) -> None:
        raise NotImplementedError()


class AttrsMutContainer(AttrsContainer):
    """This class acts as a Dict[str, PythonValue] but it's defined to access and modify
    AbstractMutVals

    Attributes:

    - type_name: The name of the object from which the attributes are being taken
    - children: Dictionary with all the references to other PythonValues
    - non_mut_attrs: Dictionary with all python references that are created on the spot,
                     i.e., Not Methods!
    - read_only: Signals whether the attributes of the AbstractMutVal are writable"""
    def __init__(
            self,
            type_name: str,
            children: 'Dict[Any, PythonValue]',
            non_mut_attrs: 'Optional[Dict[Any, Callable[[], PythonValue]]]' = None,
            read_only: bool = False
    ) -> None:
        self.type_name = type_name
        self.children = children
        self.read_only = read_only
        self.non_mut_attrs = {} if non_mut_attrs is None else non_mut_attrs

    def __getitem__(self, key_: 'Union[str, Tuple[str, Pos]]') -> PythonValue:
        if not isinstance(key_, tuple):
            key = key_
            src_pos = None  # type: Optional[Pos]
        else:
            key, src_pos = key_

        if key in self.non_mut_attrs:
            return self.non_mut_attrs[key]()

        try:
            return self.children[('attr', key)]
        except KeyError:
            TypeCheckLogger().new_warning(
                "E011",
                f"AttributeError: '{self.type_name}' object has no attribute '{key}'",
                src_pos)
            return PythonValue.top()

    def __setitem__(self,
                    key_: 'Union[str, Tuple[str, Pos]]',
                    val: PythonValue) -> None:
        if not isinstance(key_, tuple):
            key = key_
            src_pos = None  # type: Optional[Pos]
        else:
            key, src_pos = key_

        if self.read_only or key in self.non_mut_attrs:
            TypeCheckLogger().new_warning(
                "E012",
                f"AttributeError: '{self.type_name}' object attribute '{key}' is read-only",
                src_pos)
        else:
            self.children[('attr', key)] = val

    def __delitem__(self, key_: 'Union[str, Tuple[str, Pos]]') -> None:
        if not isinstance(key_, tuple):
            key = key_
            src_pos = None  # type: Optional[Pos]
        else:
            key, src_pos = key_

        if self.read_only or key in self.non_mut_attrs:
            TypeCheckLogger().new_warning(
                "E012",
                f"AttributeError: '{self.type_name}' object attribute '{key}' is read-only",
                src_pos)
        else:
            try:
                del self.children[('attr', key)]
            except KeyError:
                TypeCheckLogger().new_warning("E013", f"AttributeError: '{key}'", src_pos)


class AttrsTopContainer(AttrsContainer):
    """This class acts as a Dict[str, PythonValue] that does nothing or returns PV.top()"""
    def __getitem__(self, key_: 'Union[str, Tuple[str, Pos]]') -> PythonValue:
        return PythonValue.top()

    def __delitem__(self, key_: 'Union[str, Tuple[str, Pos]]') -> None:
        pass

    def __setitem__(self, key_: 'Union[str, Tuple[str, Pos]]', val: PythonValue) -> None:
        pass


class SubscriptsContainer(ABC):
    """This class acts as a Dict[PythonValue, PythonValue]"""
    @abstractmethod
    def __getitem__(self, key_: PythonValue) -> PythonValue:
        raise NotImplementedError()

    @abstractmethod
    def __delitem__(self, key_: PythonValue) -> None:
        raise NotImplementedError()

    @abstractmethod
    def __setitem__(self, key_: PythonValue, val: PythonValue) -> None:
        raise NotImplementedError()


class SubscriptsTopContainer(SubscriptsContainer):
    """This class acts as a Dict[PythonValue, PythonValue] but returns PV.top() or does
    nothing"""
    def __getitem__(self, key_: PythonValue) -> PythonValue:
        return PythonValue.top()

    def __delitem__(self, key_: PythonValue) -> None:
        pass

    def __setitem__(self, key_: PythonValue, val: PythonValue) -> None:
        pass
