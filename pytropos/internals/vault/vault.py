from typing import Dict, List, Optional, Set, Callable
from typing import Tuple, Union  # noqa: F401
import typing as ty
from types import ModuleType

from ..values.value import Value, Any
from ..values.function import Function
from ..values.builtin_values import Bool
from ..errors import TypeCheckLogger

from .branch_node import BranchNode
from .scope import FrozenScope, Scope
from .cell import Cell

from ..tools import Pos

import pytropos.internals.operations.unitary as unitary

__all__ = ['Vault', 'DefFunction', 'Module']


class VaultException(Exception):
    pass


class DefFunction(Function):
    # TODO(helq): extend cocoon function to return more stuff, like freevars and other
    # potentially useful data from the function
    def __init__(self,
                 fun:       Callable,
                 cell_vars: Optional[Dict[str, Cell]],
                 args:      Tuple[str, ...]
                 ) -> None:
        # Assuming that we get our function wrapped by another function which gives us the
        # nonlocals of that function:
        # def myfun():
        #   def function(*args, **kargs):
        #     vau1 = pt.Vault(vau)
        #     vau1.add_locals('i', 'x')
        #     vau1.load_args(args, kargs)
        #     return pt.add(vau1['i'], vau1['x'])
        #   return function, None, ('i', 'x')
        #
        # From:
        # def myfun(i, x):
        #   return i + x
        #
        self._fun       = fun
        self._cell_vars = cell_vars
        self._args      = args

    @property
    def co_cellvars(self) -> Optional[Dict[str, Cell]]:
        return self._cell_vars

    def call(self, *args: 'Value', src_pos: Optional[Pos] = None) -> 'Value':  # type: ignore
        # TODO(helq): several todos:
        # should save the type of the arguments passed, also, should copy the type of return
        # if the code is run again with the same parameters, we don't need to run it again.
        # Probably two different variables:
        # - What happens when the function is called with Any() arguments, does it fail?
        # - What happens if the function is called with a specific set of arguments
        # Is the function calling itself recursevely, if yes, return Any() (probably)
        return self._fun(self, *args)  # type: ignore

    def load_args(self, vau: 'Vault', params: List[Value]) -> None:
        # TODO(helq): create alert of not mismatched size between declared args and number
        # of params passed to run
        for arg, param in zip(self._args, params):
            assert arg in vau._locals_cells, "`{}` hasn't been declared as a local variable"
            vau[arg] = param


# Closure = List[Tuple[Tuple[str, ...], Scope]]
ClosureDict = Dict[int, FrozenScope]
ScopeLike = Dict[str, Value]


def extendMerge(dic: Dict[ty.Any, Set[str]], other: Dict[ty.Any, Set[str]]) -> None:
    for k, v in other.items():
        if k in dic:
            dic[k].update(v)
        else:
            dic[k] = v


class FrozenVault(object):
    def __init__(self, vault: 'Vault') -> None:
        self.is_global = vault._global
        self.global_scope = FrozenScope(vault._global_scope)
        if self.is_global:
            self.nonlocals = {}  # type: Dict[str, Union[object, None, Value]]
            self.locals = {}     # type: Dict[str, Union[object, None, Value]]
        else:
            self.nonlocals = {i: k.raw_content for i, k in vault._nonlocals_cells.items()
                              if i in vault._nonlocals}
            self.locals = {i: k.raw_content for i, k in vault._locals_cells.items()}


class Vault(object):
    # __global_vault = None  # type: Optional[Vault]
    __builtin_scope = None  # type: Dict[str, Value]

    @classmethod
    def get_builtins(cls) -> Dict[str, Value]:
        if cls.__builtin_scope is None:
            raise ValueError("No default builtins has been defined")
        return cls.__builtin_scope

    @classmethod
    def set_builtins(cls, dic: Dict[str, Value]) -> None:
        cls.__builtin_scope = dic

    def __init__(self,
                 vault=None,               # type: Union[Vault, None, Scope]
                 branch_names=['global'],  # type: List[str]
                 ) -> None:
        self._branch_names = branch_names[:]

        if vault is None:
            self._global_scope = Scope()
            self._global = True
        elif isinstance(vault, Vault):
            # making copy of vault (contains the same elements but it's a different list)
            self._global_scope = vault._global_scope
            if vault._global:
                self._nonlocals_cells = dict()  # type: Dict[str, Cell]
            else:
                self._nonlocals_cells = vault._nonlocals_cells.copy()
                self._nonlocals_cells.update(vault._locals_cells)
            self._nonlocals = set()  # type: Set[str]
            self._locals_cells = dict()  # type: Dict[str, Cell]
            self._global = False
        else:
            raise VaultException("vault must be None or a Vault object")

    # TODO(helq): check builtins!!!
    # TODO(helq): get, set and del, shouldn't raise any error, the errors should be raised
    # by Cell or Scope
    def __getitem__(self, key_: Union[str, Tuple[str, Pos]]) -> ty.Any:
        if not isinstance(key_, tuple):
            key = key_
            src_pos = None  # type: Optional[Pos]
        else:
            key, src_pos = key_

        if not self._global:
            if key in self._locals_cells:
                if self._locals_cells[key].is_there_something:
                    return self._locals_cells[key].content
                else:
                    TypeCheckLogger().new_warning(
                        "W202",
                        "The local variable `{}` isn't set".format(key),
                        src_pos
                    )
                    return Any()
            elif key in self._nonlocals_cells:
                if self._nonlocals_cells[key].is_there_something:
                    return self._nonlocals_cells[key].content
                else:
                    TypeCheckLogger().new_warning(
                        "W203",
                        "The nonlocal variable `{}` isn't set".format(key),
                        src_pos
                    )
                    return Any()

        # assuming is in global scope
        if key in self._global_scope:
            return self._global_scope[key]

        TypeCheckLogger().new_warning(
            "W201",
            "Global variable `{}` isn't set".format(key),
            src_pos
        )
        # TODO(helq): check if what was passed is a builtin, if it is, maybe
        # you should return its typing version, just to check for correctness
        # of the call of the builtin
        return Any(key)

    def __setitem__(self, key_: Union[str, Tuple[str, Pos]], value: ty.Any) -> None:
        if not isinstance(key_, tuple):
            key = key_
            src_pos = None  # type: Optional[Pos]
        else:
            key, src_pos = key_

        if not self._global:
            if key in self._nonlocals_cells:
                self._nonlocals_cells[key].content = value
                return
            elif key in self._locals_cells:
                self._locals_cells[key].content = value
                return
        self._global_scope[key] = value

    def __delitem__(self, key_: Union[str, Tuple[str, Pos]]) -> None:
        if not isinstance(key_, tuple):
            key = key_
            src_pos = None  # type: Optional[Pos]
        else:
            key, src_pos = key_

        if not self._global:
            if key in self._locals_cells:
                if self._locals_cells[key].is_there_something:
                    del self._locals_cells[key].content
                else:
                    TypeCheckLogger().new_warning(
                        "W202",
                        "The local variable `{}` has been already deleted".format(key),
                        src_pos
                    )
                return
            elif key in self._nonlocals_cells:
                if self._nonlocals_cells[key].is_there_something:
                    del self._nonlocals_cells[key].content
                else:
                    TypeCheckLogger().new_warning(
                        "W203",
                        "The nonlocal variable `{}` has been already deleted".format(key),
                        src_pos
                    )
                return
        if key in self._global_scope:
            del self._global_scope[key]
        else:
            TypeCheckLogger().new_warning(
                "W201",
                "Global variable `{}` isn't set".format(key),
                src_pos
            )

    def __contains__(self, item: str) -> bool:
        return item in self._global_scope

    def __repr__(self) -> str:
        return (
            "Vault({"
            + ', '.join(sorted(repr(k)+': '+repr(v) for k, v in self._global_scope.items()))
            + "})")

    def add_nonlocals(self, *keys: str) -> None:
        for key in keys:
            assert key not in self._locals_cells, \
                "A variable cannot be both, local and nonlocal," \
                " but `{}` is already marked as local".format(key)
            assert key in self._nonlocals_cells, \
                "The variable `{}` must be declared inside an enclosing scope".format(key)
        self._nonlocals.update(keys)

    def add_locals(self, *keys: str) -> None:
        for key in keys:
            assert key not in self._nonlocals, \
                "A variable cannot be both, local and nonlocal," \
                " but `{}` is already marked as nonlocal".format(key)
            self._locals_cells[key] = Cell()

    def get_cells(self, keys: List[str]) -> Dict[str, Cell]:
        cells = {}  # type: Dict[str, Cell]
        for key in keys:
            if key in self._nonlocals_cells:
                cells[key] = self._nonlocals_cells[key]
            elif key in self._locals_cells:
                cells[key] = self._locals_cells[key]
            else:
                raise ValueError("Variable is neither local or nonlocal in the current Vault")
        return cells

    def _run_branch(self,
                    branch: Callable[[], None],
                    branch_name: str = 'branch'
                    ) -> FrozenVault:
        self._branch_names.append(branch_name)

        BranchNode.current_branch = \
            BranchNode.current_branch.newChild('.'.join(self._branch_names))

        branch()  # running if branch code

        branch_vault = FrozenVault(self)

        assert BranchNode.current_branch.parent is not None, \
            "Error trying to come back to previous branch state, unreachable"
        BranchNode.current_branch = BranchNode.current_branch.parent

        self._branch_names.pop()

        return branch_vault

    def runIfBranching(self,
                       if_res: Value,
                       if_branch: Callable[[], None],
                       else_branch: Optional[Callable[[], None]] = None
                       ) -> None:
        assert isinstance(if_res, Value), \
            "the result of the execution of an if statement must always be a Value"

        if_bool = unitary.bool(if_res)

        if isinstance(if_bool, Bool):
            if if_bool.n is None:
                merge = True
            else:
                merge = False
        else:
            merge = True

        if_vault = self._run_branch(if_branch, 'if')
        if else_branch is None:
            if merge:
                self._mergeBranches(if_vault)
            elif if_bool.n:  # type: ignore
                self._replaceWithBranch(if_vault)
        else:
            else_vault = self._run_branch(else_branch, 'else')
            if merge:
                self._mergeBranches(if_vault, else_vault)
            elif if_bool.n:  # type: ignore
                self._replaceWithBranch(if_vault)
            else:
                self._replaceWithBranch(else_vault)

    def _mergeBranches(
            self,
            branch_l: FrozenVault,
            branch_r: Optional[FrozenVault] = None
    ) -> None:
        raise NotImplementedError

    def _replaceWithBranch(self,
                           branch: FrozenVault
                           ) -> None:
        self._global_scope.updateAndDelete(branch.global_scope)
        for k, var in branch.nonlocals.items():
            self._nonlocals_cells[k].raw_content = var
        for k, var in branch.locals.items():
            self._locals_cells[k].raw_content = var

    # to simulate * (star) import
    def load_module(self, module: ModuleType, name: str) -> None:
        mod = Module(module, name)
        for var in mod.exported_vars:
            self[var] = mod.get[var]

    def show_interior(self) -> None:
        if not self._global:
            locals_ = {k: v.raw_content for k, v in self._locals_cells.items()}
            nonlocals = {k: self._nonlocals_cells[k] for k in self._nonlocals}
            print("Local variables: {}".format(locals_))
            print("Nonlocal variables: {}".format(nonlocals))
        print("Global variables: {}".format(self._global_scope))


class Module(Value):
    def __init__(self, mod: ModuleType, name: str) -> None:
        self.module = mod
        self.name = name

    @property
    def exported_vars(self) -> List[str]:
        if hasattr(self.module, '__all__'):
            exported_vars = getattr(self.module, '__all__')  # type: List[str]
        else:
            exported_vars = [var for var in dir(self.module) if var[0] != '_']

        return exported_vars

    def __getitem__(self, key_: Union[str, Tuple[str, Pos]]) -> Value:
        if not isinstance(key_, tuple):
            key = key_
            src_pos = None  # type: Optional[Pos]
        else:
            key, src_pos = key_

        if hasattr(self.module, key):
            return getattr(self.module, key)  # type: ignore

        TypeCheckLogger().new_warning(
            "W204",
            "The module `{}` doesn't have an attribute `{}`".format(self.name, key),
            src_pos
        )
        return Any()

    def __setitem__(self, key: str, var: Value) -> None:
        raise NotImplementedError("You cannot overwrite variables inside a module yet!  Sorry")

    def __delitem__(self, key: str) -> None:
        raise NotImplementedError("You cannot overwrite variables inside a module yet!  Sorry")

    @property
    def get(self) -> 'Module':
        return self


if __name__ == "__main__":
    ld = Scope()
    ld['test'] = 20
    ld.addLayer()
    print(ld)
    ld['test'] = 10
    print(ld)
    ld.removeLayer()
    print(ld)
    del ld['test']
    ld.addLayer()
    ld['test'] = 3
    print(ld)
    ld.removeLayer()
    print(ld)

    node = BranchNode()
    n2 = node.newChild().newChild()
    n3 = node.newChild()
    print(node.findDistanceToNode(n2))
    print(n2.findDistanceToNode(node))
    print(n2.findDistanceToNode(n3))
    n4 = n2.newChild().newChild()
    n5 = n2.newChild()
    print(n4.findDistanceToNode(n4))
    print(n4.findDistanceToNode(n5))
    print(n5.findDistanceToNode(n3))
