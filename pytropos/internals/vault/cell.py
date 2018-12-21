from typing import Dict, Union, List, Optional  # noqa: F401

from ..values.base import AbstractValue

from .branch_node import BranchNode, global_branch


Deleted = object()


class Cell(object):
    # __new_id = 0  # type: int
    # All Scope's in existence!
    # Many are unreachable, usually the Garbage Collector doesn't kill them all
    # immediately. Thus, this is only an estimate of how many scopes are reachable.
    # len(__existing_ids) >= `num of reachable scopes`
    # __existing_ids = set()  # type: Set[int]

    # @classmethod
    # def __getnewid(cls) -> int:
    #     toret = cls.__new_id
    #     cls.__new_id += 1
    #     return toret

    # @property
    # def id(self) -> int:
    #     return self.__id

    def __init__(self) -> None:
        # content_layers can contain Values, None or the object Deleted (which signals the
        # variable has been deleted)
        self._content_layers = [None]  # type: List[Union[AbstractValue, None, object]]
        self.__branch = global_branch
        # self.__id = Scope.__getnewid()
        # Scope.__existing_ids.add(self.__id)
        if self.__branch != BranchNode.current_branch:
            self.__moveToNewBranch()

    # def __del__(self) -> None:
    #     # print("I'm dying T_T ({})".format(self.__id))
    #     Scope.__existing_ids.remove(self.__id)

    @property
    def raw_content(self) -> Union[AbstractValue, None, object]:
        if self.__branch != BranchNode.current_branch:
            self.__moveToNewBranch()
        for cont in reversed(self._content_layers):
            if cont is Deleted:
                return Deleted
            elif cont is not None:
                return cont
        return None

    @raw_content.setter
    def raw_content(self, val: Union[AbstractValue, None, object]) -> None:
        if self.__branch != BranchNode.current_branch:
            self.__moveToNewBranch()
        assert val is None or val is Deleted or isinstance(val, AbstractValue), \
            "The value `{}` is neither None, Deleted (an obj), or an AbstractValue".format(val)
        # print("setter", val)
        self._content_layers[-1] = val

    @property
    def is_there_something(self) -> bool:
        for cont in reversed(self._content_layers):
            if cont is Deleted:
                return False
            elif cont is not None:
                return True
        return False

    @property
    def content(self) -> AbstractValue:
        if self.__branch != BranchNode.current_branch:
            self.__moveToNewBranch()
        for cont in reversed(self._content_layers):
            if cont is Deleted:
                raise KeyError("Cell is empty. The variable has been deleted")
            elif cont is not None:
                # If the value is not None and not Deleted, then it must be a AbstractValue (or so
                # I hope)
                return cont  # type: ignore
        raise KeyError("Cell is empty. No value has been saved on it")

    @content.setter
    def content(self, content: AbstractValue) -> None:
        if self.__branch != BranchNode.current_branch:
            self.__moveToNewBranch()
        self._content_layers[-1] = content

    @content.deleter
    def content(self) -> None:
        if self.__branch != BranchNode.current_branch:
            self.__moveToNewBranch()
        # TODO(helq): show warning message if self._content_layers[-1] is Deleted
        self._content_layers[-1] = Deleted

    def __repr__(self) -> str:
        if self.__branch != BranchNode.current_branch:
            self.__moveToNewBranch()

        if self._content_layers[-1] is None or self._content_layers[-1] is Deleted:
            return "Cell()"
        return "Cell(" + repr(self._content_layers[-1]) + ")"

    def addLayer(self) -> None:
        self._content_layers.append(None)

    def removeLayer(self) -> None:
        if len(self._content_layers) == 1:
            raise Exception("Only one layer in Scope, it can't be removed")
        self._content_layers.pop()

    def layerDepth(self) -> int:
        return len(self._content_layers)

    def __moveToNewBranch(self) -> None:
        same, up, down = self.__branch.findDistanceToNode(BranchNode.current_branch)
        depth = self.layerDepth()
        if depth < same:
            for i in range(same-depth):
                self.addLayer()

        for i in range(up):
            self.removeLayer()
        for i in range(down):
            self.addLayer()

        self.__branch = BranchNode.current_branch
