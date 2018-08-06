from typing import Callable, Any, Optional, List, Union, TypeVar, Dict, Tuple
import ast
from typed_ast import ast3

from .warnings import InternalWarning, internal_warnings

__all__ = ["AstAttributeUnknown", 'to_python_ast']


class AstAttributeUnknown(Exception):
    pass


def to_python_ast(tree: ast3.AST) -> 'ast.AST':
    def helper(v: Any) -> Any:
        """
        Takes a typed_ast.AST and converts it into a python ast.AST
        """
        if isinstance(v, ast3.AST):
            fields = [f for f in v._fields if f != 'type_comment']
            klass = getattr(ast, type(v).__name__)
            return klass(**{f: to_python_ast(getattr(v, f)) for f in fields})
        elif isinstance(v, list):
            return [to_python_ast(e) for e in v]
        elif isinstance(v, (str, int, float)) or v is None:
            return v
        raise AstAttributeUnknown(
            "to_python_ast: The type '{}' is unknown to me".format(type(v)))
    return helper(tree)  # type: ignore


T = TypeVar('T')


def flatten(lst: List[Union[T, list]]) -> List[T]:
    toret: List[T] = []
    for e in lst:
        if isinstance(e, list):
            toret.extend(flatten(e))
        else:
            toret.append(e)
    return toret


# A transformation function, takes two parameters and returns them (possibly) changed
AdditionalParams = Dict[str, Any]
TransformationFun = Callable[[ast3.AST, Optional[AdditionalParams]],
                             Tuple[Union[ast3.AST, List[ast3.AST]], Optional[AdditionalParams]]]


# walk_ast(tree) returns a copy of the tree
# the function f_before and f_after take an AST and return the AST modified as they
# please, there is no need for them to traverse the structure, walk_ast does that for
# them. They are allowed to modify the structure they're given, the structure is a copy.
# The usual way to work with them is either modify the structure in place and return it,
# or create a new structure (a object inheriting of AST, like Add) and return it, both are
# valid and it will be the same result in the end.
def walk_ast(
        tree:     ast3.AST,
        f_before: Optional[TransformationFun] = None,
        f_after:  Optional[TransformationFun] = None,
        verbose:  bool = False,
        add_params: Dict[str, Any] = {},
) -> ast3.AST:

    if verbose:
        print("Type of tree:", type(tree))

    def walk_helper(v: Any, add_params: Optional[AdditionalParams]) -> Any:
        if isinstance(v, list):
            return flatten([walk_helper(x, add_params) for x in v])
        if isinstance(v, (str, int, float)) or v is None:
            return v
        if isinstance(v, ast3.AST):
            if add_params is None:
                return walk_ast(v, f_before, f_after, verbose)
            return walk_ast(v, f_before, f_after, verbose, add_params)
        raise AstAttributeUnknown("The type '{}' is unknown to me".format(type(v)))

    new_params = add_params  # type: AdditionalParams
    # walking down the tree
    if f_before is not None:
        # making a copy of the tree, let the original not be modified
        # TODO(helq): make it possible to create the copy only when necessary (how?)
        tree_copy = walk_ast(tree)
        new_tree, new_params_ = f_before(tree_copy, add_params.copy())
        new_params = add_params if new_params_ is None else new_params_
        # print(add_params)
        # print(new_params)

        assert not isinstance(new_tree, list), \
            "Error! The node transformation has produced a List of nodes," \
            " not a single node. :S"
        tree = new_tree

    klass = type(tree)
    # walking up the tree
    new_attrs = {n: walk_helper(a, new_params.copy()) for n, a in tree.__dict__.items()}

    if f_after is None:
        return klass(**new_attrs)
    else:
        new_tree, _ = f_after(klass(**new_attrs), new_params.copy())
        return new_tree  # type: ignore


# A non-complete transformation function (with additional None output)
OutputPartialTrans = Optional[Tuple[Union[ast3.AST, List[ast3.AST]], Optional[Dict[str, Any]]]]
TransformationFun_ = Callable[[ast3.AST, Optional[Dict[str, Any]]], OutputPartialTrans]


def combine_transformations(
        trans_list: List[TransformationFun_]
) -> TransformationFun:
    def new_trans(
            v: ast3.AST,
            add_params: Optional[Dict[str, Any]]
    ) -> Tuple[Union[ast3.AST, List[ast3.AST]], Optional[Dict[str, Any]]]:
        new_node = None  # type: OutputPartialTrans
        for trans in trans_list:
            new_node = trans(v, add_params)
            if new_node is not None:
                return new_node

        # To see the errors generated in execution run the code in this manner:
        # $ python -i -m tensorlint.main file.py
        # > import tensorlint.translate as tt
        # > for i in tt.internal_warnings:
        # ...  print(i)
        # This is a list of Nodes that have been totally checked!!
        if type(v) not in [ast3.Import, ast3.For, ast3.Call, ast3.AnnAssign]:
            internal_warnings.append(InternalWarning(
                "There is no rule for this kind of AST node: `{}`".format(type(v))))

        return v, add_params

    return new_trans
