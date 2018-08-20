from typing import Optional, List, Tuple
from typed_ast import ast3
import re

from .binops import operations
from .base import (
    AstAttributeUnknown,
    OutputPartialTrans,
    AddParams
)

# A non-complete transformation function (with additional None output)
# InputPartialTrans = [ast3.AST, AddParams]

# TODO(helq): add trick to documentation, use:
# > from tensorlint.translate.tools import pprint_ast_expr
# > pprint_ast_expr('expr')
# to get how to write by hand a part of the tree (AST)


def checking_add_params(
        v: ast3.AST,
        add_params: AddParams
) -> OutputPartialTrans:
    # print(ast3.dump(v))
    print("{}:".format(type(v).__name__))
    print("   ", add_params)
    return None


def augassign_transformation_before(
        v: ast3.AST,
        add_params: AddParams
) -> OutputPartialTrans:
    if isinstance(v, ast3.AugAssign):
        op = type(v.op)
        if isinstance(v.target, ast3.Name):
            left_value = ast3.Name(v.target.id, ast3.Load())  # type: ast3.expr
        elif isinstance(v.target, ast3.Attribute):
            left_value = ast3.Attribute(v.target.value, v.target.attr, ast3.Load())
        else:
            raise AstAttributeUnknown(
                "to_tensorlint: The left hand side of type '{}'"
                " inside an ast3.AugAssign is unknown to me".format(type(v.target)))
        new_v = ast3.Assign(
            targets=[v.target],
            value=ast3.BinOp(
                left=left_value,
                op=op(),
                right=v.value,
                lineno=v.lineno,
                col_offset=v.col_offset
            ),
            type_comment=None)
        return [(new_v, None)]
    return None


def num_transformation(
        v: ast3.AST,
        add_params: AddParams
) -> OutputPartialTrans:
    if isinstance(v, ast3.Num):
        if isinstance(v.n, (int, float)):
            attr = 'Int' if isinstance(v.n, int) else 'Float'
            # converting num `n` to `tl.Int(int, v.n)`
            new_v = ast3.Call(
                func=ast3.Attribute(
                    value=ast3.Name(id='tl', ctx=ast3.Load()),
                    attr=attr,
                    ctx=ast3.Load()),
                args=[ast3.Num(n=v.n)], keywords=[])
        return [(new_v, None)]
    return None


def import_transformation(
        v: ast3.AST,
        add_params: AddParams
) -> OutputPartialTrans:
    if isinstance(v, ast3.Import):
        non_supported_modules: List[str] = []
        modules_supported:    List[Tuple[str, Optional[str]]] = []
        for alias in v.names:
            if alias.name in ['numpy']:
                modules_supported.append( (alias.name, alias.asname) )  # noqa: E201,E202
            else:
                non_supported_modules.append(
                    alias.name if alias.asname is None else alias.asname
                )

        libs: List[ast3.AST] = []
        if len(modules_supported) > 0:
            libs.append(
                ast3.Import(
                    names=[ast3.alias(name='tensorlint.libs.'+name,
                                      asname=name if asname is None else asname)
                           for [name, asname] in modules_supported])
            )
            libs.extend(
                ast3.parse(  # type: ignore
                    '\n'.join([
                        "vau['{name}'] = {name}".format(name=name if asname is None else asname)
                        for name, asname in modules_supported
                    ])
                ).body
            )

        if len(non_supported_modules) > 0:
            libs.extend(
                ast3.parse(  # type: ignore
                    '\n'.join([
                        "vau['{name}'] = tl.Any()".format(name=name)
                        for name in non_supported_modules
                    ])
                ).body
            )

        # if the lib hasn't been recognized in the supported libraries, it is deleted
        if len(libs) == 0:
            return []

        return [(l, None) for l in libs]
    return None


def for_transformation(
        v: ast3.AST,
        add_params: AddParams
) -> OutputPartialTrans:
    # converting `for i in range(10)` into `with for_loop(range(10)) as (i, tl)`
    if isinstance(v, ast3.For):
        new_v = ast3.With(
            items=[
                ast3.withitem(
                    context_expr=ast3.Call(
                        func=ast3.Attribute(
                            value=ast3.Name(id='tl', ctx=ast3.Load()),
                            attr='for_loop',
                            ctx=ast3.Load()),
                        args=[v.iter],
                        keywords=[]),
                    optional_vars=v.target)],
            body=v.body,
            type_comment=None)
        return [(new_v, None)]
    return None


def binop_transformation(
        v: ast3.AST,
        add_params: AddParams
) -> OutputPartialTrans:
    if isinstance(v, ast3.BinOp):
        # Converting a binary operation `5 + a` into a function call
        # with an additional parameter `src_pos`:
        # tl.add(5, a, src_pos=(20, 5))
        # TODO(helq): allow a way to deactivate this transformation, when
        # this transformation is deactivated the resulting code is more
        # readable but it is impossible to know where was the original line
        # of code, where was the mistake
        op_type = type(v.op)
        if op_type not in operations:
            raise AstAttributeUnknown(
                "There is no rule to handle this kind of operation T_T "
                "(inside transformations): `{}`".format(type(v.op)))

        op_str = operations[op_type]

        new_v = ast3.Call(
            func=ast3.Attribute(
                value=ast3.Name(id='tl', ctx=ast3.Load()),
                attr=op_str,
                ctx=ast3.Load()),
            args=[
                v.left,
                v.right
            ],
            keywords=[
                ast3.keyword(
                    arg='src_pos',
                    value=ast3.Tuple(
                        elts=[ast3.Num(v.lineno),
                              ast3.Num(v.col_offset)],
                        ctx=ast3.Load()
                    ),
                    ctx=ast3.Load()
                )
            ])
        return [(new_v, None)]
    return None


def call_transformation(
        v: ast3.AST,
        add_params: AddParams
) -> OutputPartialTrans:
    # TODO(helq): ibid from above (deactivate this transformation)
    if isinstance(v, ast3.Call):  # and False:
        # adding an attribute to the function call `src_pos`, the position
        # of the function call in the original code
        v.keywords.append(
            ast3.keyword(
                arg='src_pos',
                value=ast3.Tuple(
                    elts=[ast3.Num(v.lineno),
                          ast3.Num(v.col_offset)],
                    ctx=ast3.Load()
                ),
                ctx=ast3.Load()
            )
        )
        return [(v, None)]
    return None


def del_annassign_transformation(
        v: ast3.AST,
        add_params: AddParams
) -> OutputPartialTrans:
    # TODO(helq): in the future, the annotation should be taken into
    # account if it is telling us something about the type of the tensor
    if isinstance(v, ast3.AnnAssign):
        new_v = ast3.Assign(targets=[v.target], value=v.value)
        return [(new_v, None)]
    return None


# TODO(helq): careful if you change something in walk, this updates the value
# in place, this is "dirty"
def del_type_comment_transformation(
        v: ast3.AST,
        add_params: AddParams
) -> OutputPartialTrans:
    # Revoming type comment
    if hasattr(v, 'type_comment'):
        setattr(v, 'type_comment', None)

        return [(v, None)]
    return None


# TODO(helq): improve how combine_transformations works. Right now, this must
# go at last, otherwise it will prevent all other transformations to occur
def put_vault_id_params(
        v: ast3.AST,
        add_params: AddParams
) -> OutputPartialTrans:
    if add_params is not None:
        if 'vault_id' not in add_params and isinstance(v, ast3.Module):
            add_params['vault_id'] = 0
            # print(new_params)
        elif isinstance(v, ast3.FunctionDef):
            add_params['vault_id'] += 1
            # print(new_params)

        if 'parent_node' not in add_params:
            add_params["parent_node"] = None
        else:
            add_params["parent_node"] = add_params["me_node"]
        add_params["me_node"] = v

        return [(v, add_params)]
    return [(v, None)]


def name_to_vault_transformation(
        v: ast3.AST,
        add_params: AddParams
) -> OutputPartialTrans:
    if isinstance(v, ast3.Name):
        assert 'vault_id' in add_params, \
            "`Name to Vault` requires `put_vault_id_params` to be executed before"

        vid = add_params['vault_id']

        if vid > 0:
            if isinstance(add_params['parent_node'], ast3.arg):
                vault_name = 'vau' + (str(vid) if vid > 1 else '')
            else:
                vault_name = 'vau' + str(vid+1)
        else:
            vault_name = 'vau'

        name = v.id

        new_v = ast3.Subscript(
            value=ast3.Name(id=vault_name, ctx=ast3.Load()),
            slice=ast3.Index(value=ast3.Str(s=name)),
            ctx=v.ctx)

        return [(new_v, None)]

    return None


trans = re.compile("transformation|params")

__all__ = [f for f in dir() if trans.match(f)]
