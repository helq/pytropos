from typing import Dict, Set, Tuple
from typing import Union, List  # noqa: F401
import typing as ty

from .branch_node import BranchNode, global_branch


# TODO(helq): implement Cell object. It should have a behaivor similar to
# `Scope`, in which it can create carry information about an object in memory
# different in each branch. The main information it can carry is how many
# references an object (and where are those references (the scopes ids)).
# It carries the information in different branches, and its updated each time
# when a scope adds it or deletes it.
# class Cell(object):
#     @property
#     def obj(self) -> ty.Any:
#         return self.__obj
#
#     def __init__(self, obj: ty.Any) -> None:
#         self.__obj = obj

# A frozen dict
class FrozenScope(dict):
    def __init__(self, dic: 'Scope') -> None:
        self.__id = dic.id
        super().__init__()
        for k, v in dic.items():
            super().__setitem__(k, v)

    @property
    def id(self) -> int:
        return self.__id

    def __setitem__(self, key: ty.Any, value: ty.Any) -> None:
        raise KeyError("No key can be set in a frozen dict")

    def __delitem__(self, key: ty.Any) -> None:
        raise KeyError("No key can be deleted in a frozen dict")

    def __repr__(self) -> str:
        return "FrozenScope(" + super().__repr__() + ")"


class Scope(object):
    __new_id = 0  # type: int
    # All Scope in existence!
    # Many are unreachable, usually the Garbage Collector doesn't kill them all
    # immediately. Thus, this is only an estimate of how many scopes (layerable
    # dict) are reachable.
    # len(__existing_ids) >= `num of reachable scopes`
    __existing_ids = set()  # type: Set[int]

    @classmethod
    def __getnewid(cls) -> int:
        toret = cls.__new_id
        cls.__new_id += 1
        return toret

    @property
    def id(self) -> int:
        return self.__id

    def __init__(self) -> None:
        self.__layers = [({}, set())]  # type: List[Tuple[Dict[str,ty.Any], Set[str]]]
        self.__branch = global_branch
        self.__id = id_ = Scope.__getnewid()
        Scope.__existing_ids.add(id_)
        if self.__branch != BranchNode.current_branch:
            self.__moveToNewBranch()

    def __del__(self) -> None:
        # print("I'm dying T_T ({})".format(self.__id))
        Scope.__existing_ids.remove(self.__id)

    def __getitem__(self, key: str) -> ty.Any:
        if self.__branch != BranchNode.current_branch:
            self.__moveToNewBranch()
        for dic, dels in reversed(self.__layers):
            if key in dels:
                raise KeyError("Key `{}` has been deleted from Scope".format(key))
            if key in dic:
                return dic[key]
        raise KeyError("Key `{}` isn't inside Scope".format(key))

    def __setitem__(self, key: str, value: ty.Any) -> None:
        if self.__branch != BranchNode.current_branch:
            self.__moveToNewBranch()
        if key in self.__layers[-1][1]:
            self.__layers[-1][1].remove(key)
        self.__layers[-1][0][key] = value

    def __delitem__(self, key: str) -> None:
        if self.__branch != BranchNode.current_branch:
            self.__moveToNewBranch()
        deleted = False
        # if key is in the last layer, remove it
        if key in self.__layers[-1][0]:
            del self.__layers[-1][0][key]
            deleted = True

        # if key appears on any other layer (not in the last because it has been
        # removed from it) then explicitely say it has been deleted
        if key in self:
            self.__layers[-1][1].add(key)
            deleted = True

        if not deleted:
            raise KeyError("Key `{}` isn't inside Scope".format(key))

    def __contains__(self, key: str) -> bool:
        if self.__branch != BranchNode.current_branch:
            self.__moveToNewBranch()
        for dic, dels in reversed(self.__layers):
            if key in dels:
                return False
            if key in dic:
                return True
        return False

    def items(self) -> ty.Iterable[Tuple[str, ty.Any]]:
        if self.__branch != BranchNode.current_branch:
            self.__moveToNewBranch()
        shown: Set[str] = set()
        for dic, dels in reversed(self.__layers):
            shown.update(dels)
            for key, value in dic.items():
                if key not in shown:
                    yield (key, value)
                    shown.add(key)

    def __repr__(self) -> str:
        return "Scope({" + ', '.join(repr(k)+': '+repr(v) for k, v in self.items()) + "})"

    def __len__(self) -> int:
        return len(list(self.items()))

    def __length_hint__(self) -> int:
        if self.__branch != BranchNode.current_branch:
            self.__moveToNewBranch()
        # if nobody has toched anything inside the implementation this method
        # should return the same as __len__
        len_ = 0
        for dic, dels in self.__layers:
            len_ += len(dic) - len(dels)
        return len_ if len_ > 0 else 0

    def __iter__(self) -> ty.Iterable[str]:
        if self.__branch != BranchNode.current_branch:
            self.__moveToNewBranch()
        shown: Set[str] = set()
        for dic, dels in reversed(self.__layers):
            shown.update(dels)
            for key, value in dic.items():
                if key not in shown:
                    yield key
                    shown.add(key)

    def addLayer(self) -> None:
        self.__layers.append( (dict(), set()) )  # noqa: E201, E202

    def removeLayer(self) -> None:
        if len(self.__layers) == 1:
            raise Exception("Only one layer in Scope, it can't be removed")
        self.__layers.pop()

    def layerDepth(self) -> int:
        return len(self.__layers)

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

    # returns if something has been modified or not
    def updateAndDelete(self, other: Dict[str, ty.Any]) -> bool:
        modified = False

        deleted = set(self.__iter__()).difference(other.__iter__())
        for d in deleted:
            del self[d]
        for k, v in other.items():
            if k not in self or id(self[k]) != id(v):
                self[k] = v
                modified = True

        if len(deleted) > 0:
            modified = True
        return modified
