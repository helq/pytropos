from math import isinf
from typing import (
    Optional, List as List_, Any, Dict, Tuple as Tuple_, Set
)

from .python_values import (
    AbstractMutVal, PythonValue, Args, AttrsContainer, AttrsMutContainer,
    SubscriptsContainer
)
from .wrappers import BuiltinMethod
from ..builtin_values import NoneType, Int
from ..abstract_value import AbstractValue
from ...errors import TypeCheckLogger

from ...miscelaneous import Pos

__all__ = ['List', 'Tuple']


class TupleOrList(AbstractMutVal):
    def __init__(self,
                 lst: 'Optional[List_[PythonValue]]' = None,
                 size: 'Optional[Tuple_[int,int]]' = None,
                 children: 'Optional[Dict[Any, PythonValue]]' = None
                 ) -> None:
        super().__init__(children=children)

        if lst is not None:
            assert children is None, "Cannot initialise TupleOrList with both a list and children"
            # Copying list to children values
            for i, val in enumerate(lst):
                self.children[('index', i)] = val

            n = len(lst)
            if size is None:
                self.size = (n, n)
            else:
                assert size[0] <= n <= size[1]
                self.size = size

        elif children is None:  # lst is None, and children is {}
            self._im_top = True
            return

        self._im_top = False

    def __eq__(self, other: Any) -> 'bool':
        if not isinstance(other, type(self)):
            return False
        if self.is_top() and other.is_top():
            return True
        return super().__eq__(other) and self.size == other.size

    def _elems(self) -> 'List_[str]':
        """Returns the representation of the internal elements of the list or tuple"""
        indices: 'List_[Tuple_[int, PythonValue]]'
        indices = sorted([
            (i[1], v)
            for i, v in self.children.items()
            if isinstance(i, tuple) and i[0] == 'index'
        ])
        # print(f"indices = {indices}")

        output = []  # type: List_[str]
        i = j = 0
        for j, v in indices:
            if i == j:
                i += 1
            else:
                i = j
                output.append(f"...")
            output.append(repr(v))

        if self.size[1] > j+1:
            output.append('...')

        return output

    @classmethod
    def top(cls) -> 'Any':
        top_name = f"_{cls.__name__}__top"
        if getattr(cls, top_name) is None:
            setattr(cls, top_name, cls())
        return getattr(cls, top_name)

    def is_top(self) -> 'bool':
        return self._im_top

    def copy_mut(self,
                 mut_heap: 'Dict[int, PythonValue]'
                 ) -> 'Any':
        if self.is_top():
            return self
        new = super().copy_mut(mut_heap)
        new.size = self.size
        return new

    def join_mut(self,
                 other: 'Any',
                 mut_heap: 'Dict[Tuple_[str, int], Tuple_[int, int, PythonValue]]',
                 ) -> 'Any':
        assert type(self) is type(other)
        new = super().join_mut(other, mut_heap)
        new.size = (min(self.size[0], other.size[0]), max(self.size[1], other.size[1]))
        return new

    def convert_into_top(self, converted: 'Set[int]') -> None:
        super().convert_into_top(converted)  # clears children too
        if hasattr(self, 'size'):
            del self.size
        self._im_top = True


class List(TupleOrList):
    __top = None  # type: List

    def __init__(self,
                 lst: 'Optional[List_[PythonValue]]' = None,
                 size: 'Optional[Tuple_[int,int]]' = None,
                 children: 'Optional[Dict[Any, PythonValue]]' = None
                 ) -> None:
        super().__init__(lst=lst, size=size, children=children)

        self.children[('attr', 'append')] = \
            PythonValue(BuiltinMethod('append', List._append, self))

    def __repr__(self) -> 'str':
        if self.is_top():
            return 'List(None)'

        if self.size[0] == self.size[1]:
            str_size = str(self.size[0])
        elif isinf(self.size[1]):
            str_size = f"[{self.size[0]},inf)"
        else:
            str_size = f"[{self.size[0]},{self.size[1]}]"

        return f'List({self.abstract_repr}, size={str_size}, id={self.mut_id})'

    @property
    def abstract_repr(self) -> 'str':
        if self.is_top():
            return 'list?'

        if self.size[1] == 0:
            return '[]'

        return '[' + ', '.join(self._elems()) + ']'

    @property
    def type_name(self) -> str:
        return "list"

    def get_attrs(self) -> 'AttrsContainer':
        return AttrsMutContainer('List', self.children, read_only=True)

    def _append(self, store: Any, args: 'Args', pos: Optional[Pos]) -> 'PythonValue':
        if len(args.vals) != 1 or args.args or args.kargs:
            if args.kargs:
                TypeCheckLogger().new_warning(
                    "E014",
                    f"TypeError: insert() takes no keyword arguments",
                    pos)
            elif args.args:
                TypeCheckLogger().new_warning(
                    "F001",
                    f"Sorry! Pytropos doesn't support calling append with a starred variable",
                    pos)
            else:
                TypeCheckLogger().new_warning(
                    "E014",
                    f"TypeError: append() takes exactly one argument ({len(args.vals)} given)",
                    pos)
            return PythonValue.top()

        if self.size[0] == self.size[1]:
            s = self.size[0]
            self.size = (s+1, s+1)
            self.children[('index', s)] = args.vals[0]
        else:
            self.size = (self.size[0]+1, self.size[1]+1)

        return PythonValue(NoneType())

    def get_subscripts(self, pos: 'Optional[Pos]') -> SubscriptsContainer:
        return SubscriptsTupleOrListContainer(self, read_only=False, pos=pos)


class Tuple(TupleOrList):
    __top = None  # type: Tuple

    def __repr__(self) -> 'str':
        if self.is_top():
            return 'Tuple(None)'

        if self.size[0] == self.size[1]:
            str_size = str(self.size[0])
        elif isinf(self.size[1]):
            str_size = f"[{self.size[0]},inf)"
        else:
            str_size = f"[{self.size[0]},{self.size[1]}]"

        return f'Tuple({self.abstract_repr}, size={str_size}, id={self.mut_id})'

    @property
    def abstract_repr(self) -> 'str':
        if self.is_top():
            return 'tuple?'

        if self.size[1] == 0:
            return '()'

        elems = self._elems()
        if len(elems) == 1:
            return f'({elems[0]},)'

        return '(' + ', '.join(elems) + ')'

    @property
    def type_name(self) -> str:
        return "tuple"

    def get_attrs(self) -> 'AttrsContainer':
        return AttrsMutContainer('Tuple', self.children, read_only=True)

    def get_subscripts(self, pos: 'Optional[Pos]') -> SubscriptsContainer:
        return SubscriptsTupleOrListContainer(self, read_only=True, pos=pos)


class SubscriptsTupleOrListContainer(SubscriptsContainer):
    """Allows to access to a specific value in the list or tuple"""
    def __init__(
            self,
            torl: TupleOrList,
            read_only: bool = False,
            pos: Optional[Pos] = None
    ) -> None:
        self.torl = torl
        self.read_only = read_only
        self.pos = pos

    def check_index(self, ival: Int) -> int:
        """Checks if the index is valid or non-valid.

        Non-valid returns:

        - -1: means that the index is outside of bounds
        - -2: means that the index is unknown, so changing the state using this index
          should invalid the list

        otherwise a number in the range [0, len(array)]"""
        if ival.is_top():
            return -2

        index = ival.val
        assert isinstance(index, int)

        size = self.torl.size

        if index < 0:
            index += size[1]
            if size[0] != size[1]:
                return -2

        if index < -1 or index >= size[1]:
            TypeCheckLogger().new_warning(
                "E017",
                f"TypeError: {self.torl.type_name} index out of range",
                self.pos)
            return -1

        return index

    def __getitem__(self, key: PythonValue) -> PythonValue:
        if key.is_top():
            return PythonValue.top()
        assert isinstance(key.val, AbstractValue)

        if not isinstance(key.val, Int):
            TypeCheckLogger().new_warning(
                "E017",
                f"TypeError: {self.torl.type_name} indices must "
                f"be integers or slices, not {key.val.type_name}",
                self.pos)
            return PythonValue.top()

        # It's an integer but we don't know which
        index = self.check_index(key.val)
        if index >= 0 and ('index', index) in self.torl.children:
            return self.torl.children['index', index]
        else:
            return PythonValue.top()

    def __delitem__(self, key: PythonValue) -> None:
        """If an error was thrown by Python, then the execution would stop (ignoring
        trycatch), thus continuing working with the same list without invalidating it is
        alright. It is not alright to allow to work on a list with an unknown deleted
        value"""
        if self.read_only:
            TypeCheckLogger().new_warning(
                "E017",
                f"TypeError: '{self.torl.type_name}' object does not support item assignment",
                self.pos)
            return

        if key.is_top():
            self.torl.convert_into_top(set())
            return
        assert isinstance(key.val, AbstractValue)

        if not isinstance(key.val, Int):
            TypeCheckLogger().new_warning(
                "E017",
                f"TypeError: {self.torl.type_name} indices must "
                f"be integers or slices, not {key.val.type_name}",
                self.pos)
            return

        # It's an integer but we don't know which
        index = self.check_index(key.val)
        if index == -2:
            self.torl.convert_into_top(set())
        elif index >= 0:
            if ('index', index) in self.torl.children:
                del self.torl.children['index', index]

            s1, s2 = self.torl.size
            self.torl.size = max(0, s1-1), max(0, s2-1)

            children = self.torl.children
            for i, v in children.copy().items():
                if isinstance(i, tuple) \
                        and i[0] == 'index' \
                        and i[1] >= index:
                    del children[i]
                    children['index', i[1]-1] = v

    def __setitem__(self, key: PythonValue, val: PythonValue) -> None:
        if self.read_only:
            TypeCheckLogger().new_warning(
                "E017",
                f"TypeError: '{self.torl.type_name}' object does not support item assignment",
                self.pos)
            return

        if key.is_top():
            self.torl.convert_into_top(set())
            return
        assert isinstance(key.val, AbstractValue)

        if not isinstance(key.val, Int):
            TypeCheckLogger().new_warning(
                "E017",
                f"TypeError: {self.torl.type_name} indices must "
                f"be integers or slices, not {key.val.type_name}",
                self.pos)
            return

        # It's an integer but we don't know which
        index = self.check_index(key.val)
        if index >= 0:
            self.torl.children['index', index] = val
        elif index == -2:
            self.torl.convert_into_top(set())
