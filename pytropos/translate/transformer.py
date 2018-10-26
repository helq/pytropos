from typing import Optional, List, Tuple, Union
from typing import Dict, Type  # noqa: F401
from typed_ast import ast3

from .tools import AstAttributeUnknown

__all__ = ['PytroposTransformer']

VisitorOutput = Union[List[ast3.AST], ast3.AST, None]

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
    # from pytropos.translate.tools import pprint_ast_expr
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


class PytroposTransformer(ast3.NodeTransformer):
    def __init__(self,
                 filename: str,
                 cursorline: Optional[int] = None
                 ) -> None:
        super().__init__()
        self.filename = filename
        self.scope_level = 0
        self.cursorline = cursorline

    @property
    def show_expr(self) -> ast3.Expr:
        return ast3.Expr(
            value=ast3.Call(
                func=ast3.Attribute(
                    value=ast3.Name(id='vau', ctx=ast3.Load()),
                    attr='show_interior', ctx=ast3.Load(),
                ),
                args=[], keywords=[])
        )

    def visit(self, node: ast3.AST) -> VisitorOutput:
        if isinstance(node, ast3.stmt):
            return self.visit_stmt(node)
        else:
            return super().visit(node)  # type: ignore

    def visit_stmt(self, node: ast3.stmt) -> VisitorOutput:
        isinline = self.cursorline is not None \
            and hasattr(node, "lineno") \
            and self.cursorline == node.lineno
        visited = super().visit(node)  # type: VisitorOutput
        if isinline:
            if isinstance(visited, list):
                return [self.show_expr] + visited  # type: ignore
            elif visited is None:
                return [self.show_expr]
            # elif isinstance(visited, ast3.AST):
            else:
                return [self.show_expr, visited]
        return visited

    def visit_AugAssign(self, node: ast3.AugAssign) -> VisitorOutput:
        op = type(node.op)
        if isinstance(node.target, ast3.Name):
            left_value = ast3.Name(node.target.id, ast3.Load())  # type: ast3.expr
        elif isinstance(node.target, ast3.Attribute):
            left_value = ast3.Attribute(node.target.value, node.target.attr, ast3.Load())
        else:
            raise AstAttributeUnknown(
                "to_pytropos: The left hand side of type '{}'"
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
            # converting num `n` to `pt.Int(int, node.n)`
            new_v = ast3.Call(
                func=ast3.Attribute(
                    value=ast3.Name(id='pt', ctx=ast3.Load()),
                    attr=attr,
                    ctx=ast3.Load()),
                args=[ast3.Num(n=node.n)], keywords=[])
            return new_v
        else:
            ...
            # TODO(helq): add warning of number type not-identified

    def visit_Import(self, node: ast3.Import) -> VisitorOutput:

        # Checking if the library being loaded is supported by pytropos
        non_supported_modules: List[str] = []
        modules_supported:    List[Tuple[str, Optional[str]]] = []
        for alias in node.names:
            if alias.name in ['numpy']:
                modules_supported.append( (alias.name, alias.asname) )  # noqa: E201,E202
            else:
                non_supported_modules.append(
                    alias.name if alias.asname is None else alias.asname
                )

        # Loading fake modules from pytropos (if supported)
        libs: List[ast3.AST] = []
        if len(modules_supported) > 0:
            libs.append(
                ast3.Import(
                    names=[ast3.alias(name='pytropos.libs.'+name,
                                      asname=name if asname is None else asname)
                           for [name, asname] in modules_supported])
            )
            libs.extend(
                ast3.parse(  # type: ignore
                    '\n'.join([
                        "vau['{name}'] = pt.Module({name}, '{name}')".format(
                            name=name if asname is None else asname
                        )
                        for name, asname in modules_supported
                    ])
                ).body
            )

        # Loading modules as Any (if not supported)
        if len(non_supported_modules) > 0:
            libs.extend(
                ast3.parse(  # type: ignore
                    '\n'.join([
                        "vau['{name}'] = pt.Any()".format(name=name)
                        for name in non_supported_modules
                    ])
                ).body
            )

        # if the lib hasn't been recognized in the supported libraries, it is deleted
        if len(libs) == 0:
            return None

        return libs

    def visit_For(self, node: ast3.For) -> VisitorOutput:
        # converting `for i in range(10)` into `with for_loop(range(10)) as (i, pt)`
        new_iter = self.visit(node.iter)
        new_target = self.visit(node.target)
        new_body = [self.visit(stmt) for stmt in node.body]
        # TODO(helq): take into account orelse body
        if len(node.orelse) > 0:
            raise AstAttributeUnknown(
                "`else` statement on a for loop hasn't been yet defined in pytropos, I'm sorry")
        new_node = ast3.With(
            items=[
                ast3.withitem(
                    context_expr=ast3.Call(
                        func=ast3.Attribute(
                            value=ast3.Name(id='pt', ctx=ast3.Load()),
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
        # pt.add(5, a, src_pos=(20, 5))
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
                value=ast3.Name(id='pt', ctx=ast3.Load()),
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
        # pt.add(5, a, src_pos=(20, 5))
        self.generic_visit(node)
        op_type = type(node.op)
        if op_type not in operations:
            raise AstAttributeUnknown(
                "There is no rule to handle this kind of operation T_T "
                "(inside transformations): `{}`".format(type(node.op)))

        op_str = operations[op_type]

        new_v = ast3.Call(
            func=ast3.Attribute(
                value=ast3.Name(id='pt', ctx=ast3.Load()),
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
        # afun.call((3,), vau, src_pos=...)
        self.generic_visit(node)

        args_ = ast3.Tuple(elts=node.args, ctx=ast3.Load())

        return ast3.Call(
            func=ast3.Attribute(
                value=node.func,
                attr='call',
                ctx=ast3.Load(),
            ),
            args=[args_, ast3.Name(id='vau', ctx=ast3.Load())],
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
        # > def function(vau):
        # >   return pt.add(vau['i'], vau['x'])
        # > vau['myfun'] = pt.DefFunction(function, None, ('i', 'x'))
        #

        # TODO(helq): (IMPORTANT) create function to detect nonlocal variables, local
        # variables and global variables
        nonlocal_vars = []  # type: List[str]

        self.scope_level += 1

        new_body: List[ast3.stmt] = []
        arg_names = [arg.arg for arg in node.args.args]

        for stmt in node.body:
            new_stmt = self.visit(stmt)
            if isinstance(new_stmt, list):
                new_body.extend(new_stmt)  # type: ignore
            elif isinstance(new_stmt, ast3.AST):
                new_body.append(new_stmt)  # type: ignore

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
                    args=[ast3.arg(arg='vau', annotation=None)],
                    vararg=None,
                    kwonlyargs=[],
                    kw_defaults=[],
                    kwarg=None,
                    defaults=[],
                ),
                body=new_body,
                decorator_list=new_decorator_list,
                returns=None,
            ),
            # vau['myfun'] = pt.DefFunction(function, None, ('i', 'x'))
            ast3.Assign(
                targets=[
                    ast3.Subscript(
                        value=ast3.Name(id='vau', ctx=ast3.Load()),
                        slice=ast3.Index(
                            value=ast3.Str(s=node.name),
                        ),
                        ctx=ast3.Store(),
                    ),
                ],
                value=ast3.Call(
                    func=ast3.Attribute(
                        value=ast3.Name(id='pt', ctx=ast3.Load()),
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
            value=ast3.Name(id='vau', ctx=ast3.Load()),
            slice=ast3.Index(
                value=varname
            ),
            ctx=node.ctx)

    def visit_Module(self, node: ast3.Module) -> VisitorOutput:
        cursorline_at_end = \
            self.cursorline is not None \
            and len(node.body) > 0 \
            and node.body[-1].lineno < self.cursorline

        self.generic_visit(node)
        node.body = (
            ast3.parse(  # type: ignore
                'import pytropos as pt\n'
                # 'pt.Any.error_when_used = True\n'
                'import pytropos.libs.base\n'
                'vau = pt.Vault()\n'
                'vau.load_module(pytropos.libs.base, "__builtins__")\n'
                'fn = {}\n'.format(repr(self.filename))
            ).body +
            node.body
        )
        if cursorline_at_end:
            node.body.append(self.show_expr)
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
                value=ast3.Name(id='pt', ctx=ast3.Load()),
                attr='Bool',
                ctx=ast3.Load(),
            ),
            args=[ast3.NameConstant(value=node.value)],
            keywords=[],
        )

    def visit_Attribute(self, node: ast3.Attribute) -> VisitorOutput:
        self.generic_visit(node)

        pos = ast3.Tuple(
            elts=[
                ast3.Str(s=node.attr),
                pos_as_tuple(node)
            ],
            ctx=ast3.Load()
        )

        return ast3.Subscript(
            value=ast3.Attribute(
                value=node.value,
                attr='get',
                ctx=ast3.Load(),
            ),
            slice=ast3.Index(
                value=pos,
            ),
            ctx=node.ctx,
        )

    def visit_Str(self, node: ast3.Str) -> VisitorOutput:
        return ast3.Call(
            func=ast3.Attribute(
                value=ast3.Name(id='pt', ctx=ast3.Load()),
                attr='Str',
                ctx=ast3.Load(),
            ),
            args=[],
            keywords=[],
        )
