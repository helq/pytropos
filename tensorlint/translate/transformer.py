from typing import Optional, List, Tuple, Union
from typing import Dict, Type  # noqa: F401
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

compopt = {
    ast3.Eq: 'eq',
    # ast3.NotEq,
    # ast3.Lt,
    # ast3.LtE,
    # ast3.Gt,
    # ast3.GtE,
    # ast3.Is,
    # ast3.IsNot,
    # ast3.In,
    # ast3.NotIn
}  # type: Dict[Type[ast3.cmpop], str]


def pos_as_tuple(node: ast3.expr) -> Optional[ast3.Tuple]:
    # from tensorlint.translate.tools import pprint_ast_expr
    # pprint_ast_expr(node)
    if not hasattr(node, 'lineno'):
        return None

    return ast3.Tuple(
        elts=[
            ast3.Tuple(
                elts=[ast3.Num(node.lineno), ast3.Num(node.col_offset)],
                ctx=ast3.Load()
            ),
            ast3.Name(id='fn', ctx=ast3.Load())
        ],
        ctx=ast3.Load()
    )


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

    def visit_Compare(self, node: ast3.Compare) -> VisitorOutput:
        # Converting a binary operation `5 + a` into a function call
        # with an additional parameter `src_pos`:
        # tl.add(5, a, src_pos=(20, 5))
        assert len(node.ops) == 1, "More than one comparison has been implemented"
        self.generic_visit(node)

        op_type = type(node.ops[0])
        if op_type not in compopt:
            raise AstAttributeUnknown(
                "There is no rule to handle this kind of operation T_T "
                "(inside transformations): `{}`".format(type(op_type)))

        op_str = compopt[op_type]

        new_v = ast3.Call(
            func=ast3.Attribute(
                value=ast3.Name(id='tl', ctx=ast3.Load()),
                attr=op_str,
                ctx=ast3.Load()),
            args=[
                node.left,
                node.comparators[0]
            ],
            keywords=[
                ast3.keyword(
                    arg='src_pos',
                    value=pos_as_tuple(node),
                    ctx=ast3.Load()
                )
            ])
        return new_v

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
                    value=pos_as_tuple(node),
                    ctx=ast3.Load()
                )
            ])
        return new_v

    def visit_Call(self, node: ast3.Call) -> VisitorOutput:
        # converting:
        # > afun(3)
        # into:
        # afun.call(3, src_pos=...)
        self.generic_visit(node)

        return ast3.Call(
            func=ast3.Attribute(
                value=node.func,
                attr='call',
                ctx=ast3.Load(),
            ),
            args=node.args,
            keywords=node.keywords + [
                ast3.keyword(
                    arg='src_pos',
                    value=pos_as_tuple(node),
                    ctx=ast3.Load()
                )
            ]
        )

    def visit_Assign(self, node: ast3.Assign) -> VisitorOutput:
        # Deleting comment annotation :S
        self.generic_visit(node)
        return ast3.Assign(targets=node.targets, value=node.value)

    def visit_AnnAssign(self, node: ast3.AnnAssign) -> VisitorOutput:
        # Deleting annotation :S
        new_node = ast3.Assign(targets=[node.target], value=node.value)
        # TODO(helq): in the future, the annotation should be taken into
        # account if it is telling us something about the type of the tensor
        self.visit(new_node)
        return new_node

    def visit_FunctionDef(self, node: ast3.FunctionDef) -> VisitorOutput:
        # Converting something like:
        #
        # > def myfun(i, x):
        # >  return i + x
        #
        # into:
        #
        # > def function(fun, *args):
        # >   vau1 = tl.Vault(vau)
        # >   vau1.add_locals('i', 'x')
        # >   fun.load_args(vau1, args)
        # >   return tl.add(vau1['i'], vau1['x'])
        # > vau['myfun'] = tl.Function(function, None, ('i', 'x'))
        #

        # TODO(helq): (IMPORTANT) create function to detect nonlocal variables, local
        # variables and global variables
        nonlocal_vars = []  # type: List[str]

        outside_vau = self.vau_name

        self.scope_level += 1

        inside_vau = self.vau_name

        new_body: List[ast3.stmt] = [
            # vau1 = tl.Vault(vau)
            ast3.Assign(
                targets=[ast3.Name(id=inside_vau, ctx=ast3.Store())],
                value=ast3.Call(
                    func=ast3.Attribute(
                        value=ast3.Name(id='tl', ctx=ast3.Load()),
                        attr='Vault',
                        ctx=ast3.Load(),
                    ),
                    args=[ast3.Name(id=outside_vau, ctx=ast3.Load())],
                    keywords=[],
                ),
            ),
        ]

        arg_names = [arg.arg for arg in node.args.args]
        if len(arg_names) > 0:
            new_body.append(
                # vau1.add_locals('i', 'x')
                ast3.Expr(
                    value=ast3.Call(
                        func=ast3.Attribute(
                            value=ast3.Name(id=inside_vau, ctx=ast3.Load()),
                            attr='add_locals',
                            ctx=ast3.Load(),
                        ),
                        args=[ast3.Str(s=arg) for arg in arg_names],
                        keywords=[],
                    ),
                )
            )

        new_body.append(
            # fun.load_args(vau1, args)
            ast3.Expr(
                value=ast3.Call(
                    func=ast3.Attribute(
                        value=ast3.Name(id='fun', ctx=ast3.Load()),
                        attr='load_args',
                        ctx=ast3.Load(),
                    ),
                    args=[
                        ast3.Name(id=inside_vau, ctx=ast3.Load()),
                        ast3.Name(id='args', ctx=ast3.Load()),
                    ],
                    keywords=[],
                ),
            )
        )

        new_body.extend([self.visit(stmt) for stmt in node.body])
        new_decorator_list = [self.visit(expr) for expr in node.decorator_list]

        # TODO(helq): Improve capture of args, there may be many types of them
        for arg in node.args.args:
            assert isinstance(arg, ast3.arg)

        self.scope_level -= 1

        if len(nonlocal_vars) == 0:
            nonlocal_vars_as_args = ast3.NameConstant(value=None)
        else:
            raise NotImplementedError("nonlocal_vars_as_args hasn't been defined yet fully")

        return [
            ast3.FunctionDef(
                name='function',
                args=ast3.arguments(
                    args=[ast3.arg(arg='fun', annotation=None)],
                    vararg=ast3.arg(arg='args', annotation=None),
                    kwonlyargs=[],
                    kw_defaults=[],
                    kwarg=None,
                    defaults=[],
                ),
                body=new_body,
                decorator_list=new_decorator_list,
                returns=None,
            ),
            # vau['myfun'] = tl.Function(function, None, ('i', 'x'))
            ast3.Assign(
                targets=[
                    ast3.Subscript(
                        value=ast3.Name(id=outside_vau, ctx=ast3.Load()),
                        slice=ast3.Index(
                            value=ast3.Str(s=node.name),
                        ),
                        ctx=ast3.Store(),
                    ),
                ],
                value=ast3.Call(
                    func=ast3.Attribute(
                        value=ast3.Name(id='tl', ctx=ast3.Load()),
                        attr='DefFunction',
                        ctx=ast3.Load(),
                    ),
                    args=[
                        ast3.Name(id='function', ctx=ast3.Load()),
                        nonlocal_vars_as_args,
                        ast3.Tuple(
                            elts=[ast3.Str(s=ar) for ar in arg_names],
                            ctx=ast3.Load(),
                        ),
                    ],
                    keywords=[],
                ),
            )
        ]

    def visit_Name(self, node: ast3.Name) -> VisitorOutput:
        # wraps the name of variable into a vault call, e.g.:
        # `var` into `vau[('var', ((21, 3), fn))]`
        pos = pos_as_tuple(node)
        if pos is not None:
            varname = ast3.Tuple(
                elts=[
                    ast3.Str(s=node.id),
                    pos
                ],
                ctx=ast3.Load()
            )  # type: ast3.expr
        else:
            varname = ast3.Str(s=node.id)

        return ast3.Subscript(
            value=ast3.Name(id=self.vau_name, ctx=ast3.Load()),
            slice=ast3.Index(
                value=varname
            ),
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

    def visit_If(self, node: ast3.If) -> VisitorOutput:
        new_test = self.visit(node.test)
        new_body = [self.visit(stmt) for stmt in node.body]
        new_orelse = [self.visit(stmt) for stmt in node.orelse]
        orelse = bool(node.orelse)

        new_node = [
            ast3.Assign(
                targets=[ast3.Name(id='if_res', ctx=ast3.Store())],
                value=new_test
            ),
            ast3.FunctionDef(
                name='if_branch',
                args=ast3.arguments(
                    args=[], vararg=None, kwonlyargs=[],
                    kw_defaults=[], kwarg=None, defaults=[]),
                body=new_body,
                decorator_list=[],
                returns=None,
            ),
        ]
        if orelse:
            new_node.append(
                ast3.FunctionDef(
                    name='else_branch',
                    args=ast3.arguments(
                        args=[], vararg=None, kwonlyargs=[],
                        kw_defaults=[], kwarg=None, defaults=[]),
                    body=new_orelse,
                    decorator_list=[],
                    returns=None,
                )
            )
        new_node.append(
            ast3.Expr(
                value=ast3.Call(
                    func=ast3.Attribute(
                        value=ast3.Name(id='vau', ctx=ast3.Load()),
                        attr='runIfBranching',
                        ctx=ast3.Load(),
                    ),
                    args=[
                        ast3.Name(id='if_res', ctx=ast3.Load()),
                        ast3.Name(id='if_branch', ctx=ast3.Load()),
                        ast3.Name(id='else_branch', ctx=ast3.Load())
                    ] if orelse else [
                        ast3.Name(id='if_res', ctx=ast3.Load()),
                        ast3.Name(id='if_branch', ctx=ast3.Load())
                    ],
                    keywords=[],
                )
            )
        )
        return new_node  # type: ignore

    # TODO(helq): Revise!!! Not all constants are of type bool
    def visit_NameConstant(self, node: ast3.NameConstant) -> VisitorOutput:
        return ast3.Call(
            func=ast3.Attribute(
                value=ast3.Name(id='tl', ctx=ast3.Load()),
                attr='Bool',
                ctx=ast3.Load(),
            ),
            args=[ast3.NameConstant(value=node.value)],
            keywords=[],
        )
