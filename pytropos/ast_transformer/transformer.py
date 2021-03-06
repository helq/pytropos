from typing import Optional, List, Union
from typing import Dict, Type, Tuple  # noqa: F401

from typed_ast import ast3

from .miscelaneous import AstTransformerError, copy_ast3

__all__ = ['PytroposTransformer', 'AstTransformerError']

VisitorOutput = Union[List[ast3.AST], ast3.AST, None]

operations = {
    ast3.Add: 'add',
    ast3.Sub: 'sub',
    ast3.Mult: 'mul',
    # ast3.MatMult: 'matmul',
    ast3.Div: 'truediv',
    ast3.FloorDiv: 'floordiv',
    ast3.Mod: 'mod',
    # __divmod__ does exist but it is not an operation, it is called by a function (divmod)
    # ast3.DivMod: '__divmod__',
    # ast3.Pow: 'pow',
    ast3.LShift: 'lshift',
    ast3.RShift: 'rshift',
    ast3.BitAnd: 'and',
    ast3.BitXor: 'xor',
    ast3.BitOr: 'or'
}

compopt = {
    # ast3.Eq: 'eq',
    # ast3.NotEq: 'ne',
    ast3.Lt: 'lt',
    ast3.LtE: 'le',
    ast3.Gt: 'gt',
    ast3.GtE: 'ge',
    # ast3.Is,
    # ast3.IsNot,
    # ast3.In,
    # ast3.NotIn
}  # type: Dict[Type[ast3.cmpop], str]

no_need_to_transform = set(operations).union(compopt).union([  # type: ignore
    # ast3.alias,
    ast3.Load,
    ast3.Store,
    ast3.Del,
])


def pos_as_tuple(node: Union[ast3.expr, ast3.stmt]) -> Optional[ast3.Tuple]:
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
                 cursorline: Optional[int] = None,
                 console: bool = False
                 ) -> None:
        super().__init__()
        self.filename = filename
        self.scope_level = 0
        self.cursorline = cursorline
        self.console = console

    _supported_modules = {'numpy': 'numpy_module',
                          'pytropos.hints.numpy': 'hints_numpy_module'}

    def _show_store_contents_expr(self) -> ast3.Expr:
        """Returns an ast3.Expr which prints the value of the store in the screen. Useful
        for debugging.
        """
        # print(st)
        return ast3.Expr(
            value=ast3.Call(
                func=ast3.Name(id='print', ctx=ast3.Load()),
                args=[ast3.Name(id='st', ctx=ast3.Load())],
                keywords=[],
            ),
        )

    def visit(self, node: ast3.AST) -> VisitorOutput:
        """Overwriting `visit` to:

        - allow it `visit_stmt`
        - throw error if a transformation hasn't been defined for a node type
        """

        isoncursor = False
        if isinstance(node, ast3.stmt):
            isoncursor = self.isoncursor(node)

        node_type = type(node)
        method_name = f'visit_{node_type.__name__}'
        if hasattr(self, method_name):
            method = getattr(self, method_name)
            if isoncursor:
                return self.add_stmt_print_store(method(node))
            else:
                return method(node)  # type: ignore

        # Ignoring supported operators (like Div, Mul, ...)
        if node_type in no_need_to_transform:
            return node
        else:
            if hasattr(node, 'lineno'):
                raise AstTransformerError(
                    f"{self.filename}:{node.lineno}:{node.col_offset}: Fatal Error:"  # type: ignore
                    f" Pytropos doesn't support {node_type.__name__!r} yet. "
                    "Sorry for the inconvinience :S"
                )
            raise AstTransformerError(
                f"Fatal Error: Pytropos doesn't support {node_type.__name__!r} yet."
                " Sorry for the inconvinience :S"
            )
        # else:
        #     return super().visit(node)  # type: ignore

    def isoncursor(self, node: ast3.stmt) -> bool:
        return self.cursorline is not None \
            and hasattr(node, "lineno") \
            and self.cursorline == node.lineno

    def add_stmt_print_store(self, node: VisitorOutput) -> VisitorOutput:
        if isinstance(node, list):
            return [self._show_store_contents_expr()] + node  # type: ignore
        elif node is None:
            return [self._show_store_contents_expr()]
        else:
            assert isinstance(node, ast3.AST)
            return [self._show_store_contents_expr(), node]

    def visit_AugAssign(self, node: ast3.AugAssign) -> VisitorOutput:
        """Converts `A (op)= Statement` into `A = A (op) (Statement)`
        """
        left_value = copy_ast3(node.target)
        left_value.ctx = ast3.Load()  # type: ignore

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
        """Wraps a number into a Pytropos type.

        Example: given the number `3` returns `pt.int(3)`
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
            raise AstTransformerError(
                f"Number of type {type(node.n)} isn't supported by pytropos. Sorry :S"
            )

    def visit_Compare(self, node: ast3.Compare) -> VisitorOutput:
        "Transforms a comparision into a function call. E.g. `ABC == MNO` into `ABC.eq(MNO)`"

        assert len(node.ops) == 1, "Pytropos only supports comparisions of two values at the time"
        self.generic_visit(node)

        op_type = type(node.ops[0])
        if op_type not in compopt:
            raise AstTransformerError(
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
        "Transforms a binary operation into a function call. E.g. `ABC == MNO` into `ABC.eq(MNO)`"

        self.generic_visit(node)
        op_type = type(node.op)
        if op_type not in operations:
            raise AstTransformerError(
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
        """Transforms an assignment with annotation into a pytropos type hint assignment.

        For example, it converts::

            var: ann = expr

        into::

            `var` = pt.type_hint(`ann`, `expr`)
        """
        if node.value is None:
            raise AstTransformerError(
                f"{self.filename}:{node.lineno}:{node.col_offset}: Fatal Error: "
                "Only annotated assignments are allowed (variables with initial values). "
                "I.e., no full support for PEP 526 yet. Sorry :("
            )

        pos = pos_as_tuple(node)

        # Deleting annotation :S
        self.generic_visit(node)
        # new_node = ast3.Assign(targets=[node.target], value=node.value)
        return ast3.Assign(
            targets=[node.target],
            value=ast3.Call(
                func=ast3.Attribute(
                    value=ast3.Name(id='pt', ctx=ast3.Load()),
                    attr='annotation',
                    ctx=ast3.Load(),
                ),
                args=[
                    node.annotation,
                    node.value,
                    pos if pos else ast3.Expr(value=ast3.NameConstant(value=None))
                ],
                keywords=[],
            ),
        )

    def visit_Name(self, node: ast3.Name) -> VisitorOutput:
        """Transforms a name lookup into a dictionary lookup.

        For example, it converts::

            var

        into::

            st[('var', ...)]
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
        "Adding the necessary pumbling for the transformed module to work"

        # In the case the transformation is being called from Console, then don't add
        # anything to it
        cursorline_at_end = \
            self.cursorline is not None \
            and len(node.body) > 0 \
            and node.body[-1].lineno < self.cursorline

        self.generic_visit(node)

        if not self.console:
            node.body = (
                ast3.parse(  # type: ignore
                    'import pytropos.internals as pt\n'
                    # 'import pytropos.libs.base\n'
                    'st = pt.Store()\n'
                    'pt.loadBuiltinFuncs(st)\n'
                    # 'st.load_module(pytropos.libs.base, "__builtins__")\n'
                    f'fn = {self.filename!r}\n'
                ).body +
                node.body
            )

        if cursorline_at_end:
            node.body.append(self._show_store_contents_expr())

        return node

    def visit_If(self, node: ast3.If) -> VisitorOutput:
        """Transforms an if statement into what Pytropos understands:

        For example, it converts::

            if question:
                body1
            else:
                body2

        into::

            if_qstn = TRANSFORMED(question)
            def if_(st):
                body1
                return st
            def else_(st):
                body2
                return st
            st = pt.runIf(st, if_qstn, if_, else_)
        """
        self.generic_visit(node)
        new_body = node.body.copy()
        new_orelse = node.orelse.copy()
        orelse = bool(node.orelse)

        new_body.append(ast3.Return(
            value=ast3.Name(id='st', ctx=ast3.Load()),
        ))

        new_node = [
            ast3.Assign(
                targets=[ast3.Name(id='if_qstn', ctx=ast3.Store())],
                value=node.test
            ),
            ast3.FunctionDef(
                name='if_',
                args=ast3.arguments(
                    args=[ast3.arg(arg='st', annotation=None)],
                    vararg=None, kwonlyargs=[],
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
                        args=[ast3.arg(arg='st', annotation=None)],
                        vararg=None, kwonlyargs=[],
                        kw_defaults=[], kwarg=None, defaults=[]),
                    body=new_orelse,
                    decorator_list=[],
                    returns=None,
                )
            )
        new_node.append(
            ast3.Assign(
                targets=[ast3.Name(id='st', ctx=ast3.Store())],
                value=ast3.Call(
                    func=ast3.Attribute(
                        value=ast3.Name(id='pt', ctx=ast3.Load()),
                        attr='runIf',
                        ctx=ast3.Load(),
                    ),
                    args=[
                        ast3.Name(id='st', ctx=ast3.Load()),
                        ast3.Name(id='if_qstn', ctx=ast3.Load()),
                        ast3.Name(id='if_', ctx=ast3.Load()),
                        ast3.Name(id='else_', ctx=ast3.Load())
                    ] if orelse else [
                        ast3.Name(id='st', ctx=ast3.Load()),
                        ast3.Name(id='if_qstn', ctx=ast3.Load()),
                        ast3.Name(id='if_', ctx=ast3.Load())
                    ],
                    keywords=[],
                )
            )
        )
        return new_node  # type: ignore

    def visit_While(self, node: ast3.While) -> VisitorOutput:
        """Transforms an if statement into what Pytropos understands:

        For example, it converts::

            while question:
                body

        into::

            if_qstn = TRANSFORMED(question)
            def while_qst(st):
                return question
            def while_(st):
                body
                return st
            st = pt.runWhile(st, while_qstn, while_)
        """
        if node.orelse:
            raise AstTransformerError(
                f"Pytropos doesn't support else statement in while loop yet, sorry :("
            )

        self.generic_visit(node)
        new_body = node.body.copy()

        new_body.append(ast3.Return(
            value=ast3.Name(id='st', ctx=ast3.Load()),
        ))

        new_node = [
            ast3.FunctionDef(
                name='while_qst',
                args=ast3.arguments(
                    args=[ast3.arg(arg='st', annotation=None)],
                    vararg=None, kwonlyargs=[],
                    kw_defaults=[], kwarg=None, defaults=[]),
                body=[ast3.Return(value=node.test)],
                decorator_list=[],
                returns=None,
            ),
            ast3.FunctionDef(
                name='while_',
                args=ast3.arguments(
                    args=[ast3.arg(arg='st', annotation=None)],
                    vararg=None, kwonlyargs=[],
                    kw_defaults=[], kwarg=None, defaults=[]),
                body=new_body,
                decorator_list=[],
                returns=None,
            ),
            ast3.Assign(
                targets=[ast3.Name(id='st', ctx=ast3.Store())],
                value=ast3.Call(
                    func=ast3.Attribute(
                        value=ast3.Name(id='pt', ctx=ast3.Load()),
                        attr='runWhile',
                        ctx=ast3.Load(),
                    ),
                    args=[
                        ast3.Name(id='st', ctx=ast3.Load()),
                        ast3.Name(id='while_qst', ctx=ast3.Load()),
                        ast3.Name(id='while_', ctx=ast3.Load())
                    ],
                    keywords=[],
                )
            )
        ]
        return new_node  # type: ignore

    def visit_NameConstant(self, node: ast3.NameConstant) -> VisitorOutput:
        """Transforms name constants (None, True, False) into Pytropos values.

        For example, it converts::

            True
            None

        into::

            pt.bool(True)
            pt.none()
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
                args=[],
                keywords=[],
            )
        else:
            raise AstTransformerError(
                f"Pytropos doesn't recognise {type(node.value)} as a constant. Sorry"
            )

    def visit_List(self, node: ast3.List) -> VisitorOutput:
        """Transforms a list into a Pytropos value.

        For example, it converts::

            [a, 5, 21]

        into::

            pt.list([st['a'], pt.int(5), pt.int(21)])"""
        self.generic_visit(node)

        return ast3.Call(
            func=ast3.Attribute(
                value=ast3.Name(id='pt', ctx=ast3.Load()),
                attr='list',
                ctx=ast3.Load(),
            ),
            args=[node],
            keywords=[],
        )

    def visit_Expr(self, node: ast3.Expr) -> VisitorOutput:
        """Only the internal parts of an Expr are modified, an Expr keeps being an Expr"""
        self.generic_visit(node)

        # In console mode ("single" for Python's compile) any expression statement should
        # print to console
        if self.console:
            return ast3.Expr(
                value=ast3.Call(
                    func=ast3.Name(id='print_console', ctx=ast3.Load()),
                    args=[node.value],
                    keywords=[],
                ),
            )

        return node

    def visit_Delete(self, node: ast3.Delete) -> VisitorOutput:
        """Delete doesn't requires to be transformed (but its contents do)."""
        self.generic_visit(node)
        return node

    def visit_Starred(self, node: ast3.Starred) -> VisitorOutput:
        """Starred doesn't requires to be transformed (but its contents do)."""
        self.generic_visit(node)
        return node

    def visit_keyword(self, node: ast3.keyword) -> VisitorOutput:
        """keyword doesn't requires to be transformed (but its contents do)."""
        self.generic_visit(node)
        return node

    def visit_Call(self, node: ast3.Call) -> VisitorOutput:
        """Transforms a call to be handled by Pytropos

        For example, it converts::

            func(3, b, *c, d=2)

        into::

            func.call(st, Args((pt.int(3), st['b']), st['c'], {'d': pt.int(2)}), pos=...)"""

        self.generic_visit(node)

        args = []  # type: List[ast3.expr]
        starred = None  # type: Optional[ast3.expr]
        kwargs_keys = []  # type: List[ast3.expr]
        kwargs_values = []  # type: List[ast3.expr]

        for i, v in enumerate(node.args):
            if isinstance(v, ast3.Starred):
                starred = v.value
                break
            args.append(v)
        # In case a starred expresion was found
        else:
            # If there is something after the starred expr
            if len(node.args) > 0 and i < len(node.args) - 1:
                raise AstTransformerError(
                    f"{self.filename}:{v.lineno}:{v.col_offset}: Fatal Error: "
                    "Only one expression starred is allowed when calling a function"
                )

        for val in node.keywords:
            if val.arg is None:
                raise AstTransformerError(
                    f"{self.filename}:{v.lineno}:{v.col_offset}: Fatal Error: "
                    "No kargs parameters is allowed when calling a function"
                )
            kwargs_keys.append(ast3.Str(s=val.arg))
            kwargs_values.append(val.value)

        new_call_args = [
            ast3.Tuple(
                elts=args,
                ctx=ast3.Load(),
            ),
        ]  # type: List[ast3.expr]

        if kwargs_keys:
            new_call_args.append(ast3.NameConstant(value=None) if starred is None else starred)
            new_call_args.append(ast3.Dict(keys=kwargs_keys, values=kwargs_values))
        elif starred is not None:
            new_call_args.append(starred)

        return ast3.Call(
            func=ast3.Attribute(
                value=node.func,
                attr='call',
                ctx=ast3.Load(),
            ),
            args=[
                ast3.Name(id='st', ctx=ast3.Load()),
                ast3.Call(
                    func=ast3.Attribute(
                        value=ast3.Name(id='pt', ctx=ast3.Load()),
                        attr='Args',
                        ctx=ast3.Load(),
                    ),
                    args=new_call_args,
                    keywords=[],
                )
            ],
            keywords=[
                ast3.keyword(
                    arg='pos',
                    value=pos_as_tuple(node),
                    ctx=ast3.Load()
                )
            ],
        )

    def visit_Attribute(self, node: ast3.Attribute) -> VisitorOutput:
        """Transforms accessing to an attribute to be handled as PythonValues do

        For example, it converts::

            expr.val

        into::

            expr.attr['val']

        or::

            expr.attr[('val', pos)]"""

        self.generic_visit(node)

        pos = pos_as_tuple(node)
        if pos is not None:
            varname = ast3.Tuple(
                elts=[
                    ast3.Str(s=node.attr),
                    pos
                ],
                ctx=ast3.Load()
            )  # type: ast3.expr
        else:
            varname = ast3.Str(s=node.attr)

        return ast3.Subscript(
            value=ast3.Attribute(
                value=node.value,
                attr='attr',
                ctx=ast3.Load(),
            ),
            slice=ast3.Index(
                value=varname,
            ),
            ctx=node.ctx,
        )

    def visit_Tuple(self, node: ast3.Tuple) -> VisitorOutput:
        """Transforms a tuple into a Pytropos value.

        For example, it converts::

            (a, 5, 21)

        into::

            pt.tuple(st['a'], pt.int(5), pt.int(21))"""
        self.generic_visit(node)

        return ast3.Call(
            func=ast3.Attribute(
                value=ast3.Name(id='pt', ctx=ast3.Load()),
                attr='tuple',
                ctx=ast3.Load(),
            ),
            args=node.elts,
            keywords=[],
        )

    def visit_Subscript(self, node: ast3.Subscript) -> VisitorOutput:
        """Transforms a subscript into something pytropos can handle

        For example, it converts::

            a[2]

        into::

            `a`.subs(pos)[`2`]
            st['a'].subs(pos)[pt.int(2)]"""
        self.generic_visit(node)

        node.value = ast3.Call(
            func=ast3.Attribute(
                value=node.value,
                attr='subs',
                ctx=ast3.Load(),
            ),
            args=[pos_as_tuple(node)],
            keywords=[],
        )

        return node

    def visit_Index(self, node: ast3.Index) -> VisitorOutput:
        """Starred doesn't requires to be transformed (but its contents do)."""
        self.generic_visit(node)
        return node

    def visit_Import(self, node: ast3.Import) -> VisitorOutput:
        """Defines how to import modules (supported and nonsupported)

        For example, it converts::

            import numpy
            import numpy as np
            import somelib, otherlib as other

        into::

            from pytropos.libs_checking import numpy_module
            st['numpy'] = numpy_module

            from pytropos.libs_checking import numpy_module
            st['np'] = numpy_module

            st['somelib'] = pt.ModuleTop
            st['other'] = pt.ModuleTop
        """

        # Checking if the library being loaded is supported by pytropos
        non_supported_modules: 'List[str]' = []
        modules_supported:     'List[Tuple[str, Optional[str]]]' = []
        for alias in node.names:
            if alias.name in self._supported_modules:
                modules_supported.append( (alias.name, alias.asname) )  # noqa: E201,E202
            else:
                non_supported_modules.append(
                    alias.name if alias.asname is None else alias.asname
                )

        # Loading fake modules from pytropos (if supported)
        libs: 'List[ast3.AST]' = []
        if len(modules_supported) > 0:
            libs.append(
                ast3.ImportFrom(
                    module='pytropos.libs_checking',
                    names=[
                        ast3.alias(name=self._supported_modules[name], asname=None)
                        for [name, asname] in modules_supported
                    ],
                    level=0,
                )
            )
            libs.extend(
                ast3.parse(  # type: ignore
                    '\n'.join([
                        f"st['{asname}'] = {self._supported_modules[name]}"
                        for name, asname in modules_supported
                    ])
                ).body
            )

        # Loading modules as Any (if not supported)
        if non_supported_modules:
            libs.extend(
                ast3.parse(  # type: ignore
                    '\n'.join([f"st['{name}'] = pt.ModuleTop" for name in non_supported_modules])
                ).body
            )

        return libs

    def visit_ImportFrom(self, node: ast3.ImportFrom) -> VisitorOutput:
        """Defines how to import (from) modules (supported and nonsupported)

        For example, it converts::

            from numpy import array
            from numpy import *
            from somelib import var, othervar as var2
            from otherlib import *

        into::

            from pytropos.libs_checking import numpy_module
            st['array'] = numpy_module.attr['array', pos...]

            from pytropos.libs_checking import numpy_module
            st.importStar(numpy_module)

            st['var'] = pt.Top
            st['var2'] = pt.Top

            st.importStar()
            """

        libs: 'List[ast3.AST]' = []

        if node.module in self._supported_modules:
            module_name = self._supported_modules[node.module]
            # from pytropos.libs_checking import module_name
            libs.append(
                ast3.ImportFrom(
                    module='pytropos.libs_checking',
                    names=[
                        ast3.alias(name=module_name, asname=None)
                    ],
                    level=0,
                )
            )
            if node.names[0].name == '*':
                # st.importStar(module_name)
                libs.append(
                    ast3.Expr(
                        value=ast3.Call(
                            func=ast3.Attribute(
                                value=ast3.Name(id='st', ctx=ast3.Load()),
                                attr='importStar',
                                ctx=ast3.Load(),
                            ),
                            args=[ast3.Name(id=module_name, ctx=ast3.Load())],
                            keywords=[],
                        ),
                    )
                )
            else:
                for alias in node.names:
                    # st['asname'] = modname.attr['name']

                    pos = pos_as_tuple(node)

                    if pos is not None:
                        attrname = ast3.Tuple(
                            elts=[
                                ast3.Str(s=alias.name),
                                pos
                            ],
                            ctx=ast3.Load()
                        )  # type: ast3.expr
                    else:
                        attrname = ast3.Str(s=alias.name)

                    libs.append(
                        ast3.Assign(
                            targets=[
                                ast3.Subscript(
                                    value=ast3.Name(id='st', ctx=ast3.Load()),
                                    slice=ast3.Index(
                                        value=ast3.Str(
                                            s=alias.asname if alias.asname else alias.name
                                        ),
                                    ),
                                    ctx=ast3.Store(),
                                ),
                            ],
                            value=ast3.Subscript(
                                value=ast3.Attribute(
                                    value=ast3.Name(id=module_name, ctx=ast3.Load()),
                                    attr='attr',
                                    ctx=ast3.Load(),
                                ),
                                slice=ast3.Index(
                                    value=attrname,
                                ),
                                ctx=ast3.Load(),
                            ),
                        )
                    )
        else:
            if node.names[0].name == '*':
                # st.importStar()
                libs.append(
                    ast3.Expr(
                        value=ast3.Call(
                            func=ast3.Attribute(
                                value=ast3.Name(id='st', ctx=ast3.Load()),
                                attr='importStar',
                                ctx=ast3.Load(),
                            ),
                            args=[],
                            keywords=[],
                        ),
                    )
                )
            else:
                libs.extend(
                    ast3.parse(  # type: ignore
                        '\n'.join([
                            "st['{asname}'] = pt.Top".format(
                                asname=alias.asname if alias.asname else alias.name
                            )
                            for alias in node.names
                        ])
                    ).body
                )

        return libs
