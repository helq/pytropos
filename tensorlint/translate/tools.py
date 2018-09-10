from typing import Any
import ast
from typed_ast import ast3

from typing import Union

__all__ = ["AstAttributeUnknown", 'pprint_ast_expr', 'to_python_ast']

# trick, use:
# > from tensorlint.translate.tools import pprint_ast_expr
# > pprint_ast_expr('expr')
# to get how to write by hand a part of the tree (AST)


class AstAttributeUnknown(Exception):
    pass


def to_python_ast(tree: ast3.AST) -> 'ast.AST':
    def helper(v: Any) -> Any:
        """
        Takes a typed_ast.AST and converts it into a python ast.AST
        """
        if isinstance(v, ast3.AST):
            klass = getattr(ast, type(v).__name__)
            return klass(**{f: to_python_ast(node) for f, node in ast3.iter_fields(v)})
        elif isinstance(v, list):
            return [to_python_ast(e) for e in v]
        elif isinstance(v, (str, int, float)) or v is None:
            return v
        raise AstAttributeUnknown(
            "to_python_ast: The type '{}' is unknown to me".format(type(v)))
    return helper(tree)  # type: ignore


def pprint_ast_expr(
        exp: Union[str, ast3.AST, ast.AST],
        only_expr: bool = True,
        fix_missing_locations: bool = False
) -> None:
    if isinstance(exp, str):
        exp = ast3.parse(exp)
        if only_expr:
            exp = exp.body[0]  # type: ignore
    if isinstance(exp, ast3.AST):
        exp = to_python_ast(exp)

    if not isinstance(exp, ast.AST):
        raise Exception("I cannot print the type {}, it isn't a type of an AST I know"
                        .format(exp))

    if fix_missing_locations:
        exp = ast.fix_missing_locations(exp)

    import astpretty
    astpretty.pprint(exp)
