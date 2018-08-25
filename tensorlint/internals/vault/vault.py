from typing import Dict, List, Optional, Set, Tuple, Callable
from typing import Union  # noqa: F401
import typing as ty
from types import ModuleType

from ..values.value import Value, Any
from ..values.builtin_values import Bool
from ..errors import TypeCheckLogger

from .branch_node import BranchNode
from .scope import FrozenScope, Scope

import tensorlint.internals.operations.unitary as unitary

__all__ = ['Vault', 'Function']


class VaultException(Exception):
    pass


class Function(Value):
    def __init__(self, fun: Callable) -> None:
        self._fun = fun
        self._closure = None  # type: Optional[Vault]
        # This is the only introspection hack that may differ between implementations of python.
        # If this doesn't work in some python implementation, this should be rewritten in "pure"
        # python, it could be very simple if a function definition gets converted into this:
        #
        # def test():
        #   vau1 = tl.Vault(vau)
        #   def myfun(*args):
        #       ...
        #   return vau1, myfun
        #
        # the code below will only need to save each paramater from the tuple into the variables
        # _closure and _fun
        if fun.__closure__ is not None and len(fun.__closure__) > 0:  # type: ignore
            assert len(fun.__closure__) == 1, (  # type: ignore
                "A function should only have a single nonlocal variable")
            clo = fun.__closure__[0].cell_contents  # type: ignore
            assert isinstance(clo, Vault), "All nonlocal variables in functions should be Vault"
            self._closure = clo

    @property
    def fun_closure(self) -> 'Optional[Vault]':
        return self._closure

    def __call__(self, *args: ty.Any, **kargs: ty.Any) -> ty.Any:
        # TODO(helq): several todos:
        # should save the type of the arguments passed, also, should copy the type of return
        # if the code is run again with the same parameters, we don't need to run it again.
        # Probably two different variables:
        # - What happens when the function is called with Any() arguments, does it fail?
        # - What happens if the function is called with a specific set of arguments
        # Is the function calling itself recursevely, if yes, return Any() (probably)
        return self._fun(*args, **kargs)


# Closure = List[Tuple[Tuple[str, ...], Scope]]
ClosureDict = Dict[int, FrozenScope]
VaultList = List[Dict[str, ty.Any]]


def extendMerge(dic: Dict[ty.Any, Set[str]], other: Dict[ty.Any, Set[str]]) -> None:
    for k, v in other.items():
        if k in dic:
            dic[k].update(v)
        else:
            dic[k] = v


class Vault(object):
    # __global_vault = None  # type: Optional[Vault]
    def __init__(self,
                 vault=None,               # type: Union[Vault, None, List[Scope]]
                 branch_names=['global'],  # type: List[str]
                 global_=None              # type: Optional[bool]
                 ) -> None:
        if global_ is not None:
            self.__global = global_   # type: bool
        self.__locals    = set()  # type: Set[str]
        self.__globals   = set()  # type: Set[str]
        self.__nonlocals = {}     # type: Dict[str, int]
        self.__branch_names = branch_names[:]

        if vault is None:
            self.__vault: List[Scope] = [Scope()]
            self.__global = True
        elif isinstance(vault, Vault):
            # making copy of vault (contains the same elements but it's a different list)
            self.__vault = vault.__vault[:]
            self.__vault.append(Scope())
            self.__global = False
        elif isinstance(vault, list) and all(isinstance(s, Scope) for s in vault):
            # making copy of vault (contains the same elements but it's a different list)
            assert len(vault) != 0, "Cannot create a vault with no scope"
            self.__vault = vault[:]
            self.__global = len(vault) == 1
        else:
            raise VaultException("vault must be None, a Vault object,"
                                 " or a list of LayerableDicts")
        # self.closures = self.__create_closures()  # type: List[Scope]
        # if Vault.__global_vault is None:
        #     Vault.__global_vault = self

    def __closuresInsideScope(self, scope: Scope, ignore: Set[int]) -> Dict[int, Scope]:
        ignore = ignore.copy()
        closures = dict()  # type: Dict[int, Scope]
        for key, val in scope.items():
            if isinstance(val, Function) and val.fun_closure is not None:
                vault = val.fun_closure
                vault_closures = vault.__getClosures(ignore)
                closures.update(vault_closures)
                ignore.update(vault_closures.keys())

        return closures

    def __getClosures(self, ignore: Optional[Set[int]] = None) -> Dict[int, Scope]:
        closures = dict()  # type: Dict[int, Scope]
        wasNone = ignore is None
        if ignore is None:
            ignore = set()
        else:
            ignore = ignore.copy()

        for scope in self.__vault:
            if scope.id not in ignore:
                closures[scope.id] = scope
                ignore.add(scope.id)

                closrs_scope = self.__closuresInsideScope(scope, ignore)
                ignore.update(closrs_scope.keys())
                closures.update(closrs_scope)

        if wasNone:
            # removing scopes to which I have direct access
            for scope in self.__vault:
                del closures[scope.id]

        return closures

    def getClosures(self) -> Dict[int, Scope]:
        return self.__getClosures()

    # TODO(helq): modify get item so we can pass later the position of the error. Maybe
    # ask for the variable together with its position, ie, key would be
    # Tuple[str, Pos] or Union[str, Tuple[str, Pos]]
    def __getitem__(self, key: str) -> ty.Any:
        # if isinstance(key, tuple):
        #     key_, src_pos = key
        # else:
        #     key_ = key
        #     src_pos = None

        if self.__global or key in self.__globals:
            scope_i = 0
        elif key in self.__nonlocals:
            assert len(self.__vault) > 2, \
                "There are not enough scopes to declare a nonlocal variable"
            scope_i = self.__nonlocals[key]
        elif key in self.__locals:
            scope_i = -1
        else:
            # assuming is in global scope
            scope_i = 0

        scope = self.__vault[scope_i]
        if key in scope:
            return scope[key]

        TypeCheckLogger().new_warning(
            "W201",
            "Variable `{}` doesn't exists in the environment".format(key),
            None
        )
        # TODO(helq): check if what was passed is a builtin, if it is, maybe
        # you should return its typing version, just to check for correctness
        # of the call of the builtin
        return Any(key)

    # TODO(helq): setitem shouldn't fail! assume global variable if it hasn't being
    # defined as nonlocal or local!
    def __setitem__(self, key: str, value: ty.Any) -> None:
        if self.__global or key in self.__locals:
            self.__vault[-1][key] = value
        elif key in self.__globals:
            self.__vault[0][key] = value
        elif key in self.__nonlocals:
            scope_i = self.__nonlocals[key]
            self.__vault[scope_i][key] = value
        else:
            raise KeyError(
                "The variable `{}` hasn't been defined as global, local or nonlocal"
                .format(key))

    def __delitem__(self, key: str) -> None:
        if self.__global or key in self.__globals:
            scope_i = 0
        elif key in self.__locals:
            scope_i = -1
        elif key in self.__nonlocals:
            scope_i = self.__nonlocals[key]
        else:
            raise KeyError(
                "The variable `{}` hasn't been defined as global, local or nonlocal"
                .format(key))

        if key in self.__vault[scope_i]:
            del self.__vault[scope_i][key]
        else:
            ...
            # TODO(helq): add warning to the list of warnings, the variable
            # cannot be deleted because it doesn't exists

    def __repr__(self) -> str:
        return "Vault([" + \
            ', '.join([
                '{'
                + ', '.join(sorted(repr(k)+': '+repr(v) for k, v in scope.items()))  # noqa: W503
                + '}'  # noqa: W503
                for scope in self.__vault
            ])+"])"

    def _run_branch(self,
                    branch: Callable[[], None],
                    branch_name: str = 'new_branch'
                    ) -> Tuple[VaultList, ClosureDict]:
        self.__branch_names.append(branch_name)

        BranchNode.current_branch = \
            BranchNode.current_branch.newChild('.'.join(self.__branch_names))

        branch()  # running if branch code

        branch_vault = (
            [FrozenScope(scope) for scope in self.__vault],  # vault copy
            {id_: FrozenScope(scope) for id_, scope in self.getClosures().items()}  # closures copy
        )

        assert BranchNode.current_branch.parent is not None, \
            "Error trying to come back to previous branch state, unreachable"
        BranchNode.current_branch = BranchNode.current_branch.parent

        self.__branch_names.pop()

        return branch_vault  # type: ignore

    def add_global(self, *keys: str) -> None:
        self.__globals.update(keys)
        for k in keys:
            assert k not in self.__nonlocals, \
                "Variable `{}` has already been declared as nonlocal".format(k)
            assert k not in self.__locals, \
                "Variable `{}` has already been declared as locals".format(k)

    def add_nonlocal(self, *keys: Tuple[str, int]) -> None:
        assert len(self.__vault) > 2, \
            "A nonlocal variable (or a closure) can only be" \
            " created when inside two levels of function declarations"
        max_depth = len(self.__vault) - 2
        for k, d in keys:
            assert 1 <= d <= max_depth, \
                "The selected scope for the nonlocal variable `{}` must be between 1 and {}," \
                " but I was given {}".format(k, max_depth, d)
            self.__nonlocals[k] = -d-1
        for k, d in keys:
            assert k not in self.__globals, \
                "Variable `{}` has already been declared as globals".format(k)
            assert k not in self.__locals, \
                "Variable `{}` has already been declared as locals".format(k)

    def add_local(self, *keys: str) -> None:
        self.__locals.update(keys)
        for k in keys:
            assert k not in self.__globals, \
                "Variable `{}` has already been declared as globals".format(k)
            assert k not in self.__nonlocals, \
                "Variable `{}` has already been declared as nonlocal".format(k)

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
            branch_l: Tuple[VaultList, ClosureDict],
            branch_r: Optional[Tuple[VaultList, ClosureDict]] = None
    ) -> None:
        raise NotImplementedError

    def _replaceWithBranch(self,
                           branch: Tuple[VaultList, ClosureDict]
                           ) -> None:
        somethingchanged = True
        # this is brute force, I don't know how to know which scopes need to be changed once
        # other some function has changed
        while somethingchanged:
            # branch.val can throw an exception if nothing has been set inside
            # of it, this often happens if you try to examine its value before
            # exiting the branch
            somethingchanged = self._replaceWithBranch_helper(branch)

    # returns true if something was modified
    def _replaceWithBranch_helper(self, branch: Tuple[VaultList, ClosureDict]) -> bool:
        modified = False

        vault, branch_closures = branch
        my_closures = self.getClosures()

        assert len(vault) == len(self.__vault), \
            "The branch's vault has a different number of scopes than myself"

        for i, scope in enumerate(self.__vault):
            mod = scope.updateAndDelete(vault[i])
            if mod:
                modified = True

        # for each closure I have access
        for vs, closure in my_closures.items():
            # If there is a frozen closure from the branch that corresponds to
            # this closure, modify closure given the frozen closure
            if closure.id in branch_closures:
                mod = closure.updateAndDelete(branch_closures[closure.id])
                if mod:
                    modified = True

        return modified

    # to simulate * (star) import
    def load_module(self, mod: ModuleType) -> None:
        if hasattr(mod, '__all__'):
            exported_vars = getattr(mod, '__all__')  # type: List[str]
        else:
            exported_vars = [var for var in dir(mod) if var[0] != '_']
        for var in exported_vars:
            self[var] = getattr(mod, var)


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
