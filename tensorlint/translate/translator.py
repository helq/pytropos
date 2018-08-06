from typed_ast import ast3

from .base import walk_ast, combine_transformations
from .transformations import (
    # checking_add_params,
    augassign_transformation_before,
    num_transformation,
    import_transformation,
    for_transformation,
    binop_transformation,
    call_transformation,
    del_annassign_transformation,
    del_type_comment_transformation,
    put_vault_id_params
)

__all__ = ["to_tensorlint"]


def to_tensorlint(tree: ast3.AST) -> ast3.AST:
    new_ast = walk_ast(
        tree,
        f_before=combine_transformations([
            augassign_transformation_before,
            put_vault_id_params,
        ]),
        f_after=combine_transformations([
            # checking_add_params,
            num_transformation,
            import_transformation,
            for_transformation,
            binop_transformation,
            call_transformation,          # can be used down or up walk
            del_annassign_transformation,     # can be executed on down and up walk
            del_type_comment_transformation,  # can be executed on down and up walk
        ]),
        verbose=False)

    # adding imports to the start of the file
    new_ast.body = (  # type: ignore
        ast3.parse(  # type: ignore
            'import tensorlint as tl\n'
            'from tensorlint.libs.base import *\n'
        ).body +
        new_ast.body)  # type: ignore
    return new_ast
