from typed_ast import ast3
from typing import Callable, Any, Optional, TypeVar

class AstAttributeUnknown(Exception):
    pass

# walk_ast(tree) returns a copy of the tree
# the function f_before and f_after take an AST and return the AST modified as they
# please, there is no need for them to traverse the structure, walk_ast does that for
# them. They are allowed to modify the structure they're given, the structure is a copy.
# The usual way to work with them is either modify the structure in place and return it,
# or create a new structure (a object inheriting of AST, like Add) and return it, both are
# valid and it will be the same result in the end.
def walk_ast(
        tree:     ast3.AST,
        f_before: Optional[Callable[[ast3.AST], ast3.AST]] = None,
        f_after:  Optional[Callable[[ast3.AST], ast3.AST]] = None,
        verbose:  bool = False
        ) -> ast3.AST:

    if verbose:
        print( "Type of tree:", type(tree) )

    def walk_helper(v: Any) -> Any:
        if isinstance(v, list):
            return [walk_helper(x) for x in v]
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
        return f_after(klass(**new_attrs))

def to_tensorlint(tree: ast3.AST) -> ast3.AST:
    def helper(v: ast3.AST) -> ast3.AST:
        # this needs to be done in the upward walk because it creates a copy of itself
        # down the tree. It would recurse indefinitely if it were executed in the downward
        # pass
        if isinstance(v, ast3.Num):
            # converting num `n` to `tl.value(int, v.n)`
            return ast3.Call(
                    func = ast3.Attribute(
                            value = ast3.Name( id='tl', ctx=ast3.Load()),
                            attr = 'value',
                            ctx = ast3.Load()),
                    args = [ast3.Name(id='int', ctx=ast3.Load()), ast3.Num(n=v.n)], keywords=[])
        elif isinstance(v, ast3.Import):
            for alias in v.names:
                if alias.name in ['numpy']:
                    sublib = alias.name
                else:
                    sublib = 'dummy'
                if alias.asname is None:
                    alias.asname = alias.name

                # TODO(helq): this is not a valid id, this creates a wrong
                # AST, but it works!! (it prints on the screen what we
                # want)
                alias.name = 'tensorlint.libs.' + sublib
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
                          optional_vars=ast3.Tuple(
                            elts=[
                              ast3.Name(id='tl', ctx=ast3.Store()),
                              ast3.Name(id='i', ctx=ast3.Store())],
                            ctx=ast3.Store()))],
                     body=v.body,
                     type_comment=None)
        return v

    # TODO(helq): add trick to documentation, use ast3.dump(ast3.parse('expr').body[0]) to
    # get how to write by hand a part of the tree (AST)
    new_ast = walk_ast(tree, f_after=helper, verbose = False)

    # adding imports to the start of the file
    new_ast.body = ( # type: ignore
        ast3.parse( # type: ignore
            'import tensorlint as tl\n'
            'from tensorlint.base import *\n'
        ).body
      + new_ast.body) # type: ignore
    return new_ast
