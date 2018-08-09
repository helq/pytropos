from typed_ast import ast3
import ast
import astpretty
from tensorlint.translate import to_python_ast

from typing import Union

__all__ = ['pprint_ast_expr']

# trick, use:
# > from tensorlint.translate.tools import pprint_ast_expr
# > pprint_ast_expr('expr')
# to get how to write by hand a part of the tree (AST)


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

    astpretty.pprint(exp)
