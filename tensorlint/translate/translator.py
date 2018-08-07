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
    put_vault_id_params,
)

__all__ = ["to_tensorlint"]


def to_tensorlint(tree: ast3.AST) -> ast3.AST:
    list_ast = walk_ast(
        tree,
        f_before=combine_transformations([[
            augassign_transformation_before,
            put_vault_id_params,
        ]]),
        f_after=combine_transformations([[
            # checking_add_params,
            num_transformation,
            import_transformation,
            for_transformation,
            binop_transformation,
            call_transformation,
        ], [
            del_annassign_transformation,
            del_type_comment_transformation,
        ]
        ]),
        verbose=False)

    assert len(list_ast) == 1, \
        "AST transformation of the module didn't give only ONE result," \
        " it gave {}".format(len(list_ast))

    new_ast = list_ast[0]

    # adding imports to the start of the file
    new_ast.body = (  # type: ignore
        ast3.parse(  # type: ignore
            'import tensorlint as tl\n'
            # 'from tensorlint.libs.base import *\n'
            'vau = tl.Vault()\n'
        ).body +  # noqa: W504
        new_ast.body)  # type: ignore
    return new_ast
