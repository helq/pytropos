from typed_ast import ast3
from typing import (
Callable, Any, Optional, List, Union, TYPE_CHECKING,
Tuple, TypeVar
)
import ast

__all__ = ["AstAttributeUnknown", "InternalWarning", "internal_warnings", "to_tensorlint"]

class AstAttributeUnknown(Exception):
    pass

def to_python_AST(tree: ast3.AST) -> 'ast.AST':
    def helper(v: Any) -> Any:
        """
        Takes a typed_ast.AST and converts it into a python ast.AST
        """
        if isinstance(v, ast3.AST):
            fields = [f for f in v._fields if f != 'type_comment']
            klass = getattr(ast, type(v).__name__)
            return klass( **{ f: to_python_AST(getattr(v, f)) for f in fields } )
        elif isinstance(v, list):
            return [to_python_AST(e) for e in v]
        elif isinstance(v, (str, int, float)) or v is None:
            return v
        raise AstAttributeUnknown("to_python_AST: The type '{}' is unknown to me".format(type(v)))
    return helper(tree) # type: ignore

T = TypeVar('T')

def flatten(lst: List[Union[T, list]]) -> List[T]:
    toret: List[T] = []
    for e in lst:
        if isinstance(e, list):
            toret.extend( flatten(e) )
        else:
            toret.append( e )
    return toret

# walk_ast(tree) returns a copy of the tree
# the function f_before and f_after take an AST and return the AST modified as they
# please, there is no need for them to traverse the structure, walk_ast does that for
# them. They are allowed to modify the structure they're given, the structure is a copy.
# The usual way to work with them is either modify the structure in place and return it,
# or create a new structure (a object inheriting of AST, like Add) and return it, both are
# valid and it will be the same result in the end.
def walk_ast(
        tree:     ast3.AST,
        f_before: Optional[Callable[[ast3.AST], Any]] = None,
        f_after:  Optional[Callable[[ast3.AST], Any]] = None,
        verbose:  bool = False
        ) -> ast3.AST:

    if verbose:
        print( "Type of tree:", type(tree) )

    def walk_helper(v: Any) -> Any:
        if isinstance(v, list):
            return flatten([walk_helper(x) for x in v])
        if isinstance(v, (str, int, float)) or v is None:
            return v
        if isinstance(v, ast3.AST):
            return walk_ast(v, f_before, f_after, verbose)
        raise AstAttributeUnknown("The type '{}' is unknown to me".format(type(v)))

    if f_before is not None:
        # making a copy of the tree, let the original not be modified
        # TODO(helq): make it possible to create the copy only when necessary (how?)
        tree_copy = walk_ast(tree)
        tree = f_before(tree_copy)

    klass = type(tree)
    new_attrs = { n:walk_helper(a) for n,a in tree.__dict__.items() }

    if f_after is None:
        return klass(**new_attrs)
    else:
        return f_after(klass(**new_attrs)) # type: ignore

class InternalWarning(object):
    msg = None # type: str
    def __init__(self, msg: str) -> None:
        self.msg = msg
    def __repr__(self) -> str:
        return "InternalWarning('"+repr(self.msg)+"')"

internal_warnings : List[InternalWarning] = []

def to_tensorlint(tree: ast3.AST) -> ast3.AST:
    def helperbefore(v: ast3.AST) -> Union[ast3.AST, List[ast3.AST]]:
        if isinstance(v, ast3.AugAssign):
            if isinstance(v.op, ast3.Add):
                if isinstance(v.target, ast3.Name):
                    left_value = ast3.Name(v.target.id, ast3.Load()) # type: ast3.expr
                elif isinstance(v.target, ast3.Attribute):
                    left_value = ast3.Attribute(v.target.value, v.target.attr, ast3.Load())
                else:
                    raise AstAttributeUnknown(
                        "to_tensorlint: The left hand side of type '{}'"
                        " inside an ast3.AugAssign is unknown to me".format(type(v.target)))
                return ast3.Assign(
                    targets=[v.target],
                    value=ast3.BinOp(
                        left=left_value,
                        op=ast3.Add(),
                        right=v.value,
                        lineno=v.lineno,
                        col_offset=v.col_offset
                    ),
                    type_comment=None)
        return v

    def helper(v: ast3.AST) -> Union[ast3.AST, List[ast3.AST]]:
        # this needs to be done in the upward walk because it creates a copy of itself
        # down the tree. It would recurse indefinitely if it were executed in the downward
        # pass
        if isinstance(v, ast3.Num):
            if isinstance(v.n, (int, float)):
                attr = 'Int' if isinstance(v.n, int) else 'Float'
                # converting num `n` to `tl.Int(int, v.n)`
                return ast3.Call(
                        func = ast3.Attribute(
                                value = ast3.Name( id='tl', ctx=ast3.Load()),
                                attr = attr,
                                ctx = ast3.Load()),
                        args = [ast3.Num(n=v.n)], keywords=[])
        elif isinstance(v, ast3.Import):
            modules_supported:    List[Tuple[str,Optional[str]]] = []
            modules_notsupported: List[Tuple[str,Optional[str]]] = []
            for alias in v.names:
                if alias.name in ['numpy']:
                    modules_supported.append( (alias.name, alias.asname) )
                else:
                    modules_notsupported.append( (alias.name, alias.asname) )

            libs: List[ast3.AST] = []
            if len(modules_supported) > 0:
                libs.append(
                  ast3.Import(
                      names=[ast3.alias(name='tensorlint.libs.'+name,
                                        asname=name if asname is None else asname)
                             for [name, asname] in modules_supported])
                )

            if len(modules_notsupported) > 0:
                libs.append(
                  ast3.ImportFrom(
                      module='tensorlint.libs.dummy',
                      names=[
                          ast3.alias(name='dummy', asname=name if asname is None else asname)
                          for [name, asname] in modules_notsupported],
                      level=0)
                )

            return libs
        # converting `for i in range(10)` into `with for_loop(range(10)) as (i, tl)`
        elif isinstance(v, ast3.For):
            return ast3.With(
                     items=[
                       ast3.withitem(
                         context_expr=ast3.Call(
                           func=ast3.Attribute(
                             value=ast3.Name(id='tl', ctx=ast3.Load()),
                             attr='for_loop',
                             ctx=ast3.Load()),
                           args=[v.iter],
                           keywords=[]),
                         optional_vars=ast3.Name(id='i', ctx=ast3.Store()))],
                     body=v.body,
                     type_comment=None)
        elif isinstance(v, ast3.BinOp):
            # Converting a binary operation `5 + a` into a function call
            # with an additional parameter `src_pos`:
            # (5).__add__(a, src_pos=(20, 5))
            # TODO(helq): allow a way to deactivate this transformation, when
            # this transformation is deactivated the resulting code is more
            # readable but it is impossible to know where was the original line
            # of code, where was the mistake
            if isinstance(v.op, ast3.Add): # and False:
                return ast3.Call(
                    func=ast3.Attribute(value=v.left, attr='__add__', ctx=ast3.Load()),
                    args=[v.right], keywords=[
                        ast3.keyword(
                            arg = 'src_pos',
                            value = ast3.Tuple(
                                elts = [ast3.Num(v.lineno),
                                        ast3.Num(v.col_offset)],
                                ctx = ast3.Load()
                            ),
                            ctx = ast3.Load()
                        ),
                        ast3.keyword(
                            arg = 'rev',
                            value = ast3.NameConstant(True),
                            ctx = ast3.Load()
                        )
                    ])
        # TODO(helq): ibid from above (deactivate this transformation)
        elif isinstance(v, ast3.Call): # and False:
            # adding an attribute to the function call `src_pos`, the position
            # of the function call in the original code
            v.keywords.append(
                ast3.keyword(
                    arg = 'src_pos',
                    value = ast3.Tuple(
                        elts = [ast3.Num(v.lineno),
                                ast3.Num(v.col_offset)],
                        ctx = ast3.Load()
                    ),
                    ctx = ast3.Load()
                )
            )
            return v
        # removing annotation from Annotated Assignment
        # TODO(helq): in the future, the annotation should be taken into
        # account if it is telling us something about the type of the tensor
        elif isinstance(v, ast3.AnnAssign):
            return ast3.Assign( targets=[v.target], value=v.value )
        # To see the errors generated in execution run the code in this manner:
        # $ python -i -m tensorlint.main file.py
        # > import tensorlint.translate as tt
        # > for i in tt.internal_warnings:
        # ...  print(i)
        internal_warnings.append( InternalWarning("There is no rule for this kind of AST node: `{}`".format(type(v))) )
        return v

    # TODO(helq): add trick to documentation, use ast3.dump(ast3.parse('expr').body[0]) to
    # get how to write by hand a part of the tree (AST)
    new_ast = walk_ast(tree, f_before=helperbefore, f_after=helper, verbose = False)

    # adding imports to the start of the file
    new_ast.body = ( # type: ignore
        ast3.parse( # type: ignore
            'import tensorlint as tl\n'
            'from tensorlint.libs.base import *\n'
        ).body
      + new_ast.body) # type: ignore
    return new_ast