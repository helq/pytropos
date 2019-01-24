from math import isinf
from typing import Optional, List as List_, Any, Dict, Tuple, Union

from .python_values import AbstractMutVal, PythonValue, Args, AttrsContainer
from .builtin_values import NoneType
from .functions import MockFunction
from ..errors import TypeCheckLogger

from ..miscelaneous import Pos

__all__ = ['List']


class List(AbstractMutVal):
    def __init__(self,
                 lst: 'Optional[List_[PythonValue]]' = None,
                 size: 'Optional[Tuple[int,int]]' = None,
                 children: 'Optional[Dict[Any, PythonValue]]' = None
                 ) -> None:
        super().__init__(children)

        if lst is not None:
            assert children is None, "Cannot initialise List with both a list and children"
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
            self.__im_top = True
            return

        self.__im_top = False

        self._attrs = {'append': PythonValue(self._append)}

    def __eq__(self, other: Any) -> 'bool':
        if not isinstance(other, List):
            return False
        if self.is_top() and other.is_top():
            return True
        return super().__eq__(other) and self.size == other.size

    def __repr__(self) -> 'str':
        if self.is_top():
            return 'List(None)'

        if self.size == 0:
            return 'List([])'

        indices: 'List_[Tuple[int, PythonValue]]'
        indices = sorted([(i[1], v) for i, v in self.children.items() if isinstance(i, tuple)])
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

        if self.size[0] == self.size[1]:
            str_size = str(self.size[0])
        elif isinf(self.size[1]):
            str_size = f"[{self.size[0]},inf)"
        else:
            str_size = f"[{self.size[0]},{self.size[1]}]"

        return 'List([' + ', '.join(output) + f'], size={str_size}, id={self.mut_id})'

    @property
    def abstract_repr(self) -> 'str':
        if self.is_top():
            return 'list?'

        if self.size == 0:
            return '[]'

        indices: 'List_[Tuple[int, PythonValue]]'
        indices = sorted([
            (i[1], v)
            for i, v in self.children.items()
            if isinstance(i, tuple)
            and i[0] == 'index'
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

        return '[' + ', '.join(output) + f']'

    __top = None  # type: List

    @classmethod
    def top(cls) -> 'List':
        if cls.__top is None:
            cls.__top = List()
        return cls.__top

    def is_top(self) -> 'bool':
        return self.__im_top

    @property
    def type_name(self) -> str:
        return "list"

    def copy_mut(self,
                 mut_heap: 'Dict[int, PythonValue]'
                 ) -> 'List':
        new = super().copy_mut(mut_heap)
        new.size = self.size
        return new  # type: ignore

    def join_mut(self,
                 other: 'List',
                 mut_heap: 'Dict[Tuple[str, int], Tuple[int, int, PythonValue]]',
                 ) -> 'List':
        new = super().join_mut(other, mut_heap)
        new.size = (min(self.size[0], other.size[0]), max(self.size[1], other.size[1]))
        return new  # type: ignore

    def get_attrs(self) -> 'AttrsContainer':
        return AttrsListContainer(self._attrs)

    @MockFunction
    def _append(self, store: Any, args: 'Args', pos: Optional[Pos]) -> 'PythonValue':
        if len(args.vals) != 1 or args.args or args.kargs:
            TypeCheckLogger().new_warning(
                "XXXX",
                f"Arguments error: ERROR YET TO DEFINE",
                pos)
            return PythonValue.top()

        if self.size[0] == self.size[1]:
            s = self.size[0]
            self.size = (s+1, s+1)
            self.children[('index', s)] = args.vals[0]
        else:
            self.size = (self.size[0]+1, self.size[1]+1)

        return PythonValue(NoneType())


# TODO(helq): Finish defining __setitem__ and __delitem__
class AttrsListContainer(AttrsContainer):
    def __init__(self, attrs: 'Dict[str, PythonValue]') -> None:
        self.attrs = attrs

    def __getitem__(self, key_: 'Union[str, Tuple[str, Pos]]') -> PythonValue:
        if not isinstance(key_, tuple):
            key = key_
            src_pos = None  # type: Optional[Pos]
        else:
            key, src_pos = key_

        try:
            return self.attrs[key]
        except KeyError:
            TypeCheckLogger().new_warning(
                "E011",
                f"AttributeError: 'list' object has no attribute '{key}'",
                src_pos)
            return PythonValue.top()
