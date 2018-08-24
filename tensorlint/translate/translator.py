from typed_ast import ast3

from .base import walk_ast, combine_transformations
from .transformations import TransformationsClass

__all__ = ["to_tensorlint"]


def to_tensorlint(tree: ast3.Module, filename: str) -> ast3.Module:
    trans = TransformationsClass(filename)
    list_ast = walk_ast(
        tree,
        f_before=combine_transformations([[
            trans.augassign_transformation_before,
        ], [
            trans.put_vault_id_params,
        ]], 'f_before'),
        f_after=combine_transformations([[
            # trans.checking_add_params,
            trans.num_transformation,
            trans.import_transformation,
            trans.for_transformation,
            trans.binop_transformation,
            trans.call_transformation,
            trans.module_transformation,
        ], [
            trans.name_to_vault_transformation,
        ], [
            trans.del_annassign_transformation,
            trans.del_type_comment_transformation,
        ]], 'f_after'),
        # ]], 'f_after', verbose=True),
        verbose=False)

    assert len(list_ast) == 1, \
        "AST transformation of the module didn't give only ONE result," \
        " it gave {}".format(len(list_ast))

    new_ast: ast3.Module
    new_ast = list_ast[0]  # type: ignore

    # adding imports to the start of the file
    return new_ast
