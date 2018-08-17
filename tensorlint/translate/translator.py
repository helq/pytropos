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
    name_to_vault_transformation
)

__all__ = ["to_tensorlint"]


def to_tensorlint(tree: ast3.Module) -> ast3.Module:
    list_ast = walk_ast(
        tree,
        f_before=combine_transformations([[
            augassign_transformation_before,
        ], [
            put_vault_id_params,
        ]], 'f_before'),
        f_after=combine_transformations([[
            # checking_add_params,
            num_transformation,
            import_transformation,
            for_transformation,
            binop_transformation,
            call_transformation,
        ], [
            name_to_vault_transformation,
        ], [
            del_annassign_transformation,
            del_type_comment_transformation,
        ]], 'f_after'),
        # ]], 'f_after', verbose=True),
        verbose=False)

    assert len(list_ast) == 1, \
        "AST transformation of the module didn't give only ONE result," \
        " it gave {}".format(len(list_ast))

    new_ast: ast3.Module
    new_ast = list_ast[0]  # type: ignore

    # adding imports to the start of the file
    new_ast.body = (
        ast3.parse(  # type: ignore
            'import tensorlint as tl\n'
            # 'tl.Any.error_when_used = True\n'
            'import tensorlint.libs.base\n'
            'vau = tl.Vault()\n'
            'vau.load_module(tensorlint.libs.base)\n'
        ).body +
        new_ast.body
    )
    return new_ast
