from typing import Any
import ast
from typed_ast import ast3

from typing import Union

__all__ = ["AstTransformerError", 'pprint_ast_expr', 'typed_ast3_to_ast']

# trick, use:
# > from pytropos.ast_transformer.miscelaneous import pprint_ast_expr
# > pprint_ast_expr('expr')
# to get how to write by hand a part of the tree (AST)
# The only problem is that no comment type information is preserved, for this, better use:
# > from typed_ast import ast3
# > ast3.dump(ast3.parse('expr').body[0])


class AstTransformerError(Exception):
    pass


def typed_ast3_to_ast(tree: ast3.AST) -> 'ast.AST':
    def helper(v: Any) -> Any:
        "Takes a `typed_ast.AST` and converts it into a python ast.AST"
        if isinstance(v, ast3.AST):
            cls = getattr(ast, type(v).__name__)
            return cls(**{f: typed_ast3_to_ast(node) for f, node in ast3.iter_fields(v)})
        elif isinstance(v, list):
            return [typed_ast3_to_ast(e) for e in v]
        elif isinstance(v, (str, int, float)) or v is None:
            return v
        raise AstTransformerError(
            "typed_ast3_to_ast: The type '{}' is unknown to me".format(type(v)))
    return helper(tree)  # type: ignore


def copy_ast3(tree: ast3.AST) -> 'ast.AST':
    def helper(v: Any) -> Any:
        "Takes a `typed_ast.AST` and converts it into a python ast.AST"
        if isinstance(v, ast3.AST):
            cls = type(v)
            new_v = cls(**{f: copy_ast3(node) for f, node in ast3.iter_fields(v)})
            if hasattr(v, 'ctx'):
                new_v.ctx = v.ctx  # type: ignore
            return ast3.copy_location(new_v, v)
        elif isinstance(v, list):
            return [copy_ast3(e) for e in v]
        elif isinstance(v, (str, int, float)) or v is None:
            return v
        raise AstTransformerError(
            "typed_ast3_to_ast: The type '{}' is unknown to me".format(type(v)))
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
        exp = typed_ast3_to_ast(exp)

    if not isinstance(exp, ast.AST):
        raise Exception("I cannot print the type {}, it isn't a type of an AST I know"
                        .format(exp))

    if fix_missing_locations:
        exp = ast.fix_missing_locations(exp)

    import astpretty
    astpretty.pprint(exp)
