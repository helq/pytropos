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
AddParams = Dict[str, Any]
OutputTrans = List[Tuple[ast3.AST, AddParams]]
OutputPartialTrans = Optional[List[Tuple[ast3.AST, Optional[AddParams]]]]
TransPartialFun = Callable[[ast3.AST, AddParams], OutputPartialTrans]
TransformationFun = Callable[[ast3.AST, AddParams], OutputTrans]


def copy_tree(tree: ast3.AST) -> ast3.AST:

    def copy_helper(v: Any) -> Any:
        if isinstance(v, list):
            return flatten([copy_helper(x) for x in v])
        if isinstance(v, (str, int, float)) or v is None:
            return v
        if isinstance(v, ast3.AST):
            return copy_tree(v)
        raise AstAttributeUnknown("The type '{}' is unknown to me".format(type(v)))

    klass = type(tree)
    # walking up the tree
    new_attrs = {n: copy_helper(a) for n, a in tree.__dict__.items()}

    return klass(**new_attrs)


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
) -> List[ast3.AST]:

    if verbose:
        print("Type of tree:", type(tree))

    def walk_helper(v: Any, add_params: AddParams) -> Any:
        if isinstance(v, list):
            return flatten([walk_helper(x, add_params) for x in v])
        if isinstance(v, (str, int, float)) or v is None:
            return v
        if isinstance(v, ast3.AST):
            list_ast = walk_ast(v, f_before, f_after, verbose, add_params)

            if len(list_ast) == 1:
                return list_ast[0]
            else:
                return list_ast

        raise AstAttributeUnknown("The type '{}' is unknown to me".format(type(v)))

    # while walking down the tree
    if f_before is not None:
        # making a copy of the tree, let the original not be modified
        # TODO(helq): make it possible to create the copy only when necessary (how?)
        tree_copy = copy_tree(tree)
        new_trees = f_before(tree_copy, add_params.copy())
        # print(add_params)
        # print(new_params)
    else:
        new_trees = [(tree, add_params)]

    trees_to_ret = []  # type: List[ast3.AST]
    for tree_, params in new_trees:
        klass = type(tree_)

        # while walking up the tree
        # creating a new node with the old parameters
        # print("About to apply transformations to {}".format(tree_.__dict__.items()))
        new_attrs = {n: walk_helper(a, params.copy()) for n, a in tree_.__dict__.items()}

        new_node = klass(**new_attrs)

        if f_after is None:
            trees_to_ret.append(new_node)
        else:
            more_new_trees = f_after(new_node, params.copy())
            trees_to_ret.extend([t for t, _ in more_new_trees])

    return trees_to_ret


def applyPartialTrans(
        trans_fun: TransPartialFun,
        nodes: List[Tuple[bool, ast3.AST, AddParams]]
) -> Optional[List[Tuple[bool, ast3.AST, AddParams]]]:
    transformed = False
    new_nodes = []  # type: List[Tuple[bool, ast3.AST, AddParams]]
    for node in nodes:
        trans, v, params = node
        if trans:
            new_nodes.append(node)
        else:
            new_node = trans_fun(v, params)
            # No change on node, the node remains in the list
            if new_node is None:
                new_nodes.append(node)
            # Node changed for another (possibly others) node,
            # the list may be empty, deleting the node
            else:
                transformed = True
                new_nodes.extend([
                    (True, v_, params if params_ is None else params_)
                    for v_, params_ in new_node])

    if transformed:
        return new_nodes
    return None


# complexity warning doesn't get raised if all code related to verbose is deleted
def combine_transformations(  # noqa: C901
        trans_list_list: List[List[TransPartialFun]],
        name: str,
        verbose: bool = False
) -> TransformationFun:
    def new_trans(
            v: ast3.AST,
            add_params: Dict[str, Any]
    ) -> OutputTrans:
        transformed = False

        # the first boolean value tells us if some transformation has been done on the node
        output = [(False, v, add_params)]  # type: List[Tuple[bool, ast3.AST, AddParams]]

        if verbose:
            print()
            print("applying transformations: {}".format(name))
            print("initial {}".format([(t, ast3.dump(v_), pms) for t, v_, pms in output]))

        for trans_list in trans_list_list:
            # if some node has been transformed, reseting its value to not
            # transformed to try a new transformation list
            if transformed:
                output = [(False, v_, pms) for _, v_, pms in output]
            for trans_fun in trans_list:
                new_output = applyPartialTrans(trans_fun, output)
                if verbose:
                    print("function: {}".format(trans_fun.__name__))

                if new_output is not None:
                    if verbose:
                        print("after conversion {}"
                              .format([(t, ast3.dump(v_), pms) for t, v_, pms in new_output]))
                    output = new_output
                    transformed = True

                    all_transformed = all(t for t, _, _ in output)
                    if all_transformed:
                        # Now that all nodes have been transformed, stop trying more transformations
                        break

        if transformed:
            final = [(v_, pms) for _, v_, pms in output]
            if verbose:
                print("modification to return: {}"
                      .format([(t, ast3.dump(v_), pms) for t, v_, pms in output]))
            return final

        # To see the errors generated in execution run the code in this manner:
        # $ python -i -m tensorlint.main file.py
        # > import tensorlint.translate as tt
        # > for i in tt.internal_warnings:
        # ...  print(i)
        # This is a list of Nodes that have been totally checked!!
        if type(v) not in [ast3.Import, ast3.For, ast3.Call, ast3.AnnAssign]:
            internal_warnings.append(InternalWarning(
                "There is no rule for this kind of AST node: `{}`".format(type(v))))

        if verbose:
            print("modification to return (no change): {}".format([(ast3.dump(v), add_params)]))
        return [(v, add_params)]

    return new_trans
