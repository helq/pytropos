from typing import Dict, List, Optional, Set, Tuple
from typing import Union  # noqa: F401
import typing as ty
from types import ModuleType

from ..value import Value, Any

from .branch_node import BranchNode
from .scope import FrozenScope, Scope


class Function(Value):
    def __init__(self, fun: ty.Callable) -> None:
        self.__fun = fun
        self.__closure = None  # type: Optional[Vault]
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
        # __closure and __fun
        if fun.__closure__ is not None and len(fun.__closure__) > 0:  # type: ignore
            assert len(fun.__closure__) == 1, (  # type: ignore
                "A function should only have a single nonlocal variable")
            clo = fun.__closure__[0].cell_contents  # type: ignore
            assert isinstance(clo, Vault), "All nonlocal variables in functions should be Vault"
            self.__closure = clo

    @property
    def fun_closure(self) -> 'Optional[Vault]':
        return self.__closure

    def __call__(self, *args: ty.Any, **kargs: ty.Any) -> ty.Any:
        # TODO(helq): several todos:
        # should save the type of the arguments passed, also, should copy the type of return
        # if the code is run again with the same parameters, we don't need to run it again.
        # Probably two different variables:
        # - What happens when the function is called with Any() arguments, does it fail?
        # - What happens if the function is called with a specific set of arguments
        # Is the function calling itself recursevely, if yes, return Any() (probably)
        return self.__fun(*args, **kargs)


T = ty.TypeVar('T')


class Ptr(ty.Generic[T]):
    def __init__(self, val: Optional[T] = None) -> None:
        self.__val = val

    @property
    def val(self) -> T:
        if self.__val is None:
            raise Exception("There is no value to return yet,"
                            " you haven't yet (probably) exited the scope")
        return self.__val

    @val.setter
    def val(self, val: T) -> None:
        self.__val = val


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
        self.__branch_diff = []   # type: List[Ptr[Tuple[VaultList, ClosureDict]]]
        self.__branch_names = branch_names[:]
        self.__next_branch_name = None  # type: Optional[str]
        # self.childVaults = set()  # type: Set[Vault]
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
            raise Exception("vault must be None, a Vault object,"
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

    def __getitem__(self, key: str) -> ty.Any:
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
            # TODO(helq): add warning!!!
            # raise KeyError(
            #     "The variable `{}` hasn't been defined as global, local or nonlocal"
            #     .format(key))

        scope = self.__vault[scope_i]
        if key in scope:
            return scope[key]

        # TODO(helq): an error should be added to the list of errors, because
        # this variable doesn't exist
        # TODO(helq): check if what was passed is a builtin, if it is, maybe
        # you should return its typing version, just to check for correctness
        # of the call of the builtin
        return Any(key)

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

    def newBranch(self, branch_name: str) -> 'Vault':
        self.__next_branch_name = branch_name
        return self

    def __enter__(self) -> Ptr[Tuple[VaultList, ClosureDict]]:
        # print("Entering vault")
        if self.__next_branch_name is None:
            self.__branch_names.append('new_branch')
        else:
            self.__branch_names.append(self.__next_branch_name)
            self.__next_branch_name = None
        BranchNode.current_branch = \
            BranchNode.current_branch.newChild('.'.join(self.__branch_names))
        # assert self.__branch_diff is None, "A branch diff is inside of Vault, shouldn't be"
        self.__branch_diff.append(Ptr())
        return self.__branch_diff[-1]

    def __exit__(self, exc_type, exc_value, traceback) -> Optional[bool]:  # type: ignore
        # TODO(helq): check if something has been changed from the original vault
        assert len(self.__branch_diff) != 0, \
            "Branch diff dissapeared, there is no way I can" \
            " return the vault modifications done inside the branch"
        self.__branch_diff[-1].val = (
            [FrozenScope(scope) for scope in self.__vault],  # vault copy
            {id_: FrozenScope(scope) for id_, scope in self.getClosures().items()}  # closures copy
        )
        self.__branch_diff.pop()
        assert BranchNode.current_branch.parent is not None, \
            "Error trying to come back to previous branch state, unreachable"
        BranchNode.current_branch = BranchNode.current_branch.parent
        assert len(self.__branch_names) > 1, \
            "There should be at least one branch name in the list of branch names"
        self.__branch_names.pop()

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

    # TODO(helq): before performing this, check all objects manipulated inherit
    # from Value, if not, something went terribly wrong!
    def replaceWithBranch(self,
                          branch: Ptr[Tuple[VaultList, ClosureDict]]
                          ) -> None:
        somethingchanged = True
        # this is brute force, I don't know how to know which scopes need to be changed once
        # other some function has changed
        while somethingchanged:
            # branch.val can throw an exception if nothing has been set inside
            # of it, this often happens if you try to examine its value before
            # exiting the branch
            somethingchanged = self.__replaceWithBranch(branch.val)

    # returns true if something was modified
    def __replaceWithBranch(self, branch: Tuple[VaultList, ClosureDict]) -> bool:
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
