from typing import Optional, List, Union
from typing import Dict, Type  # noqa: F401

from typed_ast import ast3

from .miscelaneous import AstAttributeUnknown

__all__ = ['PytroposTransformer']

VisitorOutput = Union[List[ast3.AST], ast3.AST, None]

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
    # ast3.Eq: 'eq',
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

    def _show_store_contents_expr(self) -> ast3.Expr:
        """
        Returns an ast3.Expr which prints the value of the store in the screen. Useful for
        debugging.

        > print(st)
        """
        return ast3.Expr(
            value=ast3.Call(
                func=ast3.Name(id='print', ctx=ast3.Load()),
                args=[ast3.Name(id='st', ctx=ast3.Load())],
                keywords=[],
            ),
        )

    def visit(self, node: ast3.AST) -> VisitorOutput:
        """
        Overwriting `visit` to:
        - allow visit_stmt
        - throw error if a transformation hasn't been defined for a node type
        """
        if isinstance(node, ast3.stmt):
            return self.visit_stmt(node)

        node_type = type(node)
        method_name = f'visit_{node_type.__name__}'
        if hasattr(self, method_name):
            return getattr(self, method_name)(node)  # type: ignore

        # Ignoring supported operators (like Div, Mul, ...)
        if node_type in set(operations).union(compopt):  # type: ignore
            return node
        else:
            raise AstAttributeUnknown(
                f"Pytropos doesn't support {node_type.__name__!r} yet. "
                "Sorry for the inconvinience :S"
            )
        # else:
        #     return super().visit(node)  # type: ignore

    def visit_stmt(self, node: ast3.stmt) -> VisitorOutput:
        # Checking if the current stmt is in the line cursorline passed by the user
        isinline = self.cursorline is not None \
            and hasattr(node, "lineno") \
            and self.cursorline == node.lineno

        visited = super().visit(node)  # type: VisitorOutput

        # If the user asked for to print the Store contents at this line, add the new
        # print expr
        if isinline:
            if isinstance(visited, list):
                return [self._show_store_contents_expr()] + visited  # type: ignore
            elif visited is None:
                return [self._show_store_contents_expr()]
            else:
                assert isinstance(visited, ast3.AST)
                return [self._show_store_contents_expr(), visited]

        return visited

    def visit_AugAssign(self, node: ast3.AugAssign) -> VisitorOutput:
        """
        Converting:
        > A *= X+B
        into
        > A = A*(X+B)
        """
        if isinstance(node.target, ast3.Name):
            left_value = ast3.Name(
                node.target.id, ast3.Load(),
                lineno=node.lineno,
                col_offset=node.col_offset
            )  # type: ast3.expr
        elif isinstance(node.target, ast3.Attribute):
            left_value = ast3.Attribute(
                node.target.value, node.target.attr, ast3.Load(),
                lineno=node.lineno,
                col_offset=node.col_offset
            )
        else:
            # TODO(helq): allow arbitrary expr to be set at the left side
            # All there is to do is to clone node.target and modify ctx from Store to Load
            raise AstAttributeUnknown("Error: Sorry I don't support left operands that "
                                      "are not a name at the left side of an += (or *=, ...)")

        new_target = self.visit(node.target)
        new_value = self.visit_BinOp(ast3.BinOp(
            left=left_value,
            op=node.op,
            right=node.value,
            lineno=node.lineno,
            col_offset=node.col_offset
        ))
        return ast3.Assign(
            targets=[new_target],
            value=new_value,
            type_comment=None)  # TODO(helq): don't ignore the type comment!

    def visit_Num(self, node: ast3.Num) -> VisitorOutput:
        """
        Converting:
        > 3
        into:
        pt.int(3)
        """
        if isinstance(node.n, (int, float)):
            attr = 'int' if isinstance(node.n, int) else 'float'
            new_v = ast3.Call(
                func=ast3.Attribute(
                    value=ast3.Name(id='pt', ctx=ast3.Load()),
                    attr=attr,
                    ctx=ast3.Load()),
                args=[ast3.Num(n=node.n)], keywords=[])
            return new_v
        else:
            raise AstAttributeUnknown(
                f"Number of type {type(node.n)} isn't supported by pytropos. Sorry :S"
            )

    def visit_Compare(self, node: ast3.Compare) -> VisitorOutput:
        """
        Converting:
        > ABC == MNO
        into:
        > ABC.eq(MNO)
        """
        assert len(node.ops) == 1, "Pytropos only supports comparisions of two values at the time"
        self.generic_visit(node)

        op_type = type(node.ops[0])
        if op_type not in compopt:
            raise AstAttributeUnknown(
                f"Pytropos doesn't support the comparison {type(op_type)} yet, sorry :("
            )

        op_str = compopt[op_type]

        new_v = ast3.Call(
            func=ast3.Attribute(
                value=node.left,
                attr=op_str,
                ctx=ast3.Load()),
            args=[
                node.comparators[0]
            ],
            keywords=[
                ast3.keyword(
                    arg='pos',
                    value=pos_as_tuple(node),
                    ctx=ast3.Load()
                )
            ])
        return new_v

    def visit_BinOp(self, node: ast3.BinOp) -> VisitorOutput:
        """
        Converting:
        > ABC + MNO
        into:
        > ABC.add(MNO, pos=...)
        """
        self.generic_visit(node)
        op_type = type(node.op)
        if op_type not in operations:
            raise AstAttributeUnknown(
                f"Pytropos doesn't support the operation {type(op_type)} yet, sorry :("
            )

        op_str = operations[op_type]

        new_v = ast3.Call(
            func=ast3.Attribute(
                value=node.left,
                attr=op_str,
                ctx=ast3.Load()),
            args=[
                node.right
            ],
            keywords=[
                ast3.keyword(
                    arg='pos',
                    value=pos_as_tuple(node),
                    ctx=ast3.Load()
                )
            ])
        return new_v

    def visit_Assign(self, node: ast3.Assign) -> VisitorOutput:
        # Deleting comment annotation :S
        self.type_comment = None
        self.generic_visit(node)
        return node

    def visit_AnnAssign(self, node: ast3.AnnAssign) -> VisitorOutput:
        # Deleting annotation :S
        new_node = ast3.Assign(targets=[node.target], value=node.value)
        self.visit(new_node)
        return new_node

    def visit_Name(self, node: ast3.Name) -> VisitorOutput:
        """
        Convertion:
        > var
        into:
        > st[('var', ...)]
        """
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
            value=ast3.Name(id='st', ctx=ast3.Load()),
            slice=ast3.Index(
                value=varname
            ),
            ctx=node.ctx)

    def visit_Module(self, node: ast3.Module) -> VisitorOutput:
        """
        Adding the necessary pumbling for the transformed module to work
        """
        cursorline_at_end = \
            self.cursorline is not None \
            and len(node.body) > 0 \
            and node.body[-1].lineno < self.cursorline

        self.generic_visit(node)
        node.body = (
            ast3.parse(  # type: ignore
                'import pytropos as pt\n'
                # 'import pytropos.libs.base\n'
                'st = pt.Store()\n'
                # 'st.load_module(pytropos.libs.base, "__builtins__")\n'
                f'fn = {self.filename!r}\n'
            ).body +
            node.body
        )
        if cursorline_at_end:
            node.body.append(self._show_store_contents_expr())
        return node

    def visit_If(self, node: ast3.If) -> VisitorOutput:
        """
        Converts:
        > if question:
        >     body1
        > else:
        >     body2
        into:
        > if_qstn = TRANSFORMED(question)
        > def if_(st):
        >     body1
        >     return st
        > def else_(st):
        >     body2
        >     return st
        > pt.runIf(st, if_qstn, if_, else_)
        """
        new_test = self.visit(node.test)
        new_body = [self.visit(stmt) for stmt in node.body]
        new_orelse = [self.visit(stmt) for stmt in node.orelse]
        orelse = bool(node.orelse)

        new_body.append(ast3.Return(
            value=ast3.Name(id='st', ctx=ast3.Load()),
        ))

        new_node = [
            ast3.Assign(
                targets=[ast3.Name(id='if_qstn', ctx=ast3.Store())],
                value=new_test
            ),
            ast3.FunctionDef(
                name='if_',
                args=ast3.arguments(
                    args=[], vararg=None, kwonlyargs=[],
                    kw_defaults=[], kwarg=None, defaults=[]),
                body=new_body,
                decorator_list=[],
                returns=None,
            ),
        ]
        if orelse:
            # adding "return st"
            new_orelse.append(ast3.Return(
                value=ast3.Name(id='st', ctx=ast3.Load()),
            ))
            new_node.append(
                ast3.FunctionDef(
                    name='else_',
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
                        value=ast3.Name(id='pt', ctx=ast3.Load()),
                        attr='runIf',
                        ctx=ast3.Load(),
                    ),
                    args=[
                        ast3.Name(id='if_qstn', ctx=ast3.Load()),
                        ast3.Name(id='if_', ctx=ast3.Load()),
                        ast3.Name(id='else_', ctx=ast3.Load())
                    ] if orelse else [
                        ast3.Name(id='if_qstn', ctx=ast3.Load()),
                        ast3.Name(id='if_', ctx=ast3.Load())
                    ],
                    keywords=[],
                )
            )
        )
        return new_node  # type: ignore

    def visit_NameConstant(self, node: ast3.NameConstant) -> VisitorOutput:
        """
        Converting:
        > True             or    None
        into:
        > pt.bool(True)    or    pt.none()
        """
        if isinstance(node.value, bool):
            return ast3.Call(
                func=ast3.Attribute(
                    value=ast3.Name(id='pt', ctx=ast3.Load()),
                    attr='bool',
                    ctx=ast3.Load(),
                ),
                args=[ast3.NameConstant(value=node.value)],
                keywords=[],
            )
        elif node.value is None:
            return ast3.Call(
                func=ast3.Attribute(
                    value=ast3.Name(id='pt', ctx=ast3.Load()),
                    attr='none',
                    ctx=ast3.Load(),
                ),
                keywords=[],
            )
        else:
            raise AstAttributeUnknown(
                f"Pytropos doesn't recognise {type(node.value)} as a constant. Sorry"
            )
