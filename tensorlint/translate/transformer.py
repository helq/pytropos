from typing import Optional, List, Tuple, Union
from typed_ast import ast3

from .tools import AstAttributeUnknown

__all__ = ['TensorlintTransformer']

VisitorOutput = Union[List[ast3.AST], ast3.AST, None]

# TODO(helq): add trick to documentation, use:
# > from tensorlint.translate.tools import pprint_ast_expr
# > pprint_ast_expr('expr')
# to get how to write by hand a part of the tree (AST)

# TODO(helq): remove type comments

operations = {
    ast3.Add: 'add',
    ast3.Sub: 'sub',
    ast3.Mult: 'mul',
    ast3.MatMult: 'matmul',
    ast3.Div: 'truediv',
    ast3.FloorDiv: 'floordiv',
    ast3.Mod: 'mod',
    # __divmod__ does exist but it is not an operation, it is called by a function (divmod)
    # ast3.DivMod: '__divmod__',
    ast3.Pow: 'pow',
    ast3.LShift: 'lshift',
    ast3.RShift: 'rshift',
    ast3.BitAnd: 'and',
    ast3.BitXor: 'xor',
    ast3.BitOr: 'or'
}


class TensorlintTransformer(ast3.NodeTransformer):
    def __init__(self, filename: str) -> None:
        super().__init__()
        self.filename = filename
        self.scope_level = 0

    @property
    def vau_name(self) -> str:
        if self.scope_level > 0:
            return 'vau{}'.format(self.scope_level)
        else:
            return 'vau'

    def visit_AugAssign(self, node: ast3.AugAssign) -> VisitorOutput:
        op = type(node.op)
        if isinstance(node.target, ast3.Name):
            left_value = ast3.Name(node.target.id, ast3.Load())  # type: ast3.expr
        elif isinstance(node.target, ast3.Attribute):
            left_value = ast3.Attribute(node.target.value, node.target.attr, ast3.Load())
        else:
            raise AstAttributeUnknown(
                "to_tensorlint: The left hand side of type '{}'"
                " inside an ast3.AugAssign is unknown to me".format(type(node.target)))
        new_target = self.visit(node.target)
        new_value = self.visit_BinOp(ast3.BinOp(
            left=left_value,
            op=op(),
            right=node.value,
            lineno=node.lineno,
            col_offset=node.col_offset
        ))
        return ast3.Assign(
            targets=[new_target],
            value=new_value,
            type_comment=None)  # TODO(helq): don't ignore the type comment!

    def visit_Num(self, node: ast3.Num) -> VisitorOutput:
        if isinstance(node.n, (int, float)):
            attr = 'Int' if isinstance(node.n, int) else 'Float'
            # converting num `n` to `tl.Int(int, node.n)`
            new_v = ast3.Call(
                func=ast3.Attribute(
                    value=ast3.Name(id='tl', ctx=ast3.Load()),
                    attr=attr,
                    ctx=ast3.Load()),
                args=[ast3.Num(n=node.n)], keywords=[])
            return new_v
        else:
            ...
            # TODO(helq): add warning of number type not-identified

    def visit_Import(self, node: ast3.Import) -> VisitorOutput:
        non_supported_modules: List[str] = []
        modules_supported:    List[Tuple[str, Optional[str]]] = []
        for alias in node.names:
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
            return None

        return libs

    def visit_For(self, node: ast3.For) -> VisitorOutput:
        # converting `for i in range(10)` into `with for_loop(range(10)) as (i, tl)`
        new_iter = self.visit(node.iter)
        new_target = self.visit(node.target)
        new_body = [self.visit(stmt) for stmt in node.body]
        # TODO(helq): take into account orelse body
        if len(node.orelse) > 0:
            raise AstAttributeUnknown(
                "`else` statement on a for loop hasn't been yet defined in tensorlint, I'm sorry")
        new_node = ast3.With(
            items=[
                ast3.withitem(
                    context_expr=ast3.Call(
                        func=ast3.Attribute(
                            value=ast3.Name(id='tl', ctx=ast3.Load()),
                            attr='for_loop',
                            ctx=ast3.Load()),
                        args=[new_iter],
                        keywords=[]),
                    optional_vars=new_target)],
            body=new_body,
            type_comment=None)
        return new_node

    def visit_BinOp(self, node: ast3.BinOp) -> VisitorOutput:
        # Converting a binary operation `5 + a` into a function call
        # with an additional parameter `src_pos`:
        # tl.add(5, a, src_pos=(20, 5))
        self.generic_visit(node)
        op_type = type(node.op)
        if op_type not in operations:
            raise AstAttributeUnknown(
                "There is no rule to handle this kind of operation T_T "
                "(inside transformations): `{}`".format(type(node.op)))

        op_str = operations[op_type]

        new_v = ast3.Call(
            func=ast3.Attribute(
                value=ast3.Name(id='tl', ctx=ast3.Load()),
                attr=op_str,
                ctx=ast3.Load()),
            args=[
                node.left,
                node.right
            ],
            keywords=[
                ast3.keyword(
                    arg='src_pos',
                    value=ast3.Tuple(
                        elts=[
                            ast3.Tuple(
                                elts=[ast3.Num(node.lineno), ast3.Num(node.col_offset)],
                                ctx=ast3.Load()
                            ),
                            ast3.Name(id='fn', ctx=ast3.Load())
                        ],
                        ctx=ast3.Load()
                    ),
                    ctx=ast3.Load()
                )
            ])
        return new_v

    def visit_Call(self, node: ast3.Call) -> VisitorOutput:
        # adding an attribute to the function call `src_pos`, the position
        # of the function call in the original code
        self.generic_visit(node)
        node.keywords.append(  # TODO(helq): create a new node, don't copy
            ast3.keyword(
                arg='src_pos',
                value=ast3.Tuple(
                    elts=[
                        ast3.Tuple(
                            elts=[ast3.Num(node.lineno),
                                  ast3.Num(node.col_offset)],
                            ctx=ast3.Load()
                        ),
                        ast3.Name(id='fn', ctx=ast3.Load())
                    ],
                    ctx=ast3.Load()
                ),
                ctx=ast3.Load()
            )
        )
        return node

    def visit_AnnAssign(self, node: ast3.AnnAssign) -> VisitorOutput:
        # Deleting annotation :S
        new_node = ast3.Assign(targets=[node.target], value=node.value)
        # TODO(helq): in the future, the annotation should be taken into
        # account if it is telling us something about the type of the tensor
        self.visit(new_node)
        return new_node

    def visit_FunctionDef(self, node: ast3.FunctionDef) -> VisitorOutput:
        self.scope_level += 1
        for stmt in node.body:
            self.visit(stmt)
        for expr in node.decorator_list:
            self.visit(expr)
        self.scope_level -= 1
        return [
            node,
            # ast3.Assign(
            #     targets=[
            #         ast3.Subscript(
            #             value=ast3.Name(id=self.vau_name, ctx=ast3.Load()),
            #             slice=ast3.Index(
            #                 value=ast3.Str(s=node.name),
            #             ),
            #             ctx=ast3.Store(),
            #         ),
            #     ],
            #     value=ast3.Name(id=node.name, ctx=ast3.Load()),
            # )
        ]

    def visit_Name(self, node: ast3.Name) -> VisitorOutput:
        return ast3.Subscript(
            value=ast3.Name(id=self.vau_name, ctx=ast3.Load()),
            slice=ast3.Index(value=ast3.Str(s=node.id)),
            ctx=node.ctx)

    def visit_Module(self, node: ast3.Module) -> VisitorOutput:
        self.generic_visit(node)
        node.body = (
            ast3.parse(  # type: ignore
                'import tensorlint as tl\n'
                # 'tl.Any.error_when_used = True\n'
                'import tensorlint.libs.base\n'
                'vau = tl.Vault()\n'
                'vau.load_module(tensorlint.libs.base)\n'
                'fn = {}\n'.format(repr(self.filename))
            ).body +
            node.body
        )
        return node
