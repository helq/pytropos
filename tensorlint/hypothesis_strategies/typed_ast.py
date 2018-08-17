"""
Generating random ASTs based on hypothesis. This module is only called when testing.

Python 3.6 (type commented) Grammar, taken from:
https://github.com/python/typed_ast/blob/89242344f18f94dc109823c0732325033264e22b/ast3/Parser/Python.asdl

module Python
{
    mod = Module(stmt* body, type_ignore *type_ignores)
        | Interactive(stmt* body)
        | Expression(expr body)
        | FunctionType(expr* argtypes, expr returns)

        -- not really an actual node but useful in Jython's typesystem.
        | Suite(stmt* body)

    stmt = FunctionDef(identifier name, arguments args,
                       stmt* body, expr* decorator_list, expr? returns, string? type_comment)
          | AsyncFunctionDef(identifier name, arguments args,
                             stmt* body, expr* decorator_list, expr? returns, string? type_comment)

          | ClassDef(identifier name,
             expr* bases,
             keyword* keywords,
             stmt* body,
             expr* decorator_list)
          | Return(expr? value)

          | Delete(expr* targets)
          | Assign(expr* targets, expr value, string? type_comment)
          | AugAssign(expr target, operator op, expr value)
          -- 'simple' indicates that we annotate simple name without parens
          | AnnAssign(expr target, expr annotation, expr? value, int simple)

          -- use 'orelse' because else is a keyword in target languages
          | For(expr target, expr iter, stmt* body, stmt* orelse, string? type_comment)
          | AsyncFor(expr target, expr iter, stmt* body, stmt* orelse, string? type_comment)
          | While(expr test, stmt* body, stmt* orelse)
          | If(expr test, stmt* body, stmt* orelse)
          | With(withitem* items, stmt* body, string? type_comment)
          | AsyncWith(withitem* items, stmt* body, string? type_comment)

          | Raise(expr? exc, expr? cause)
          | Try(stmt* body, excepthandler* handlers, stmt* orelse, stmt* finalbody)
          | Assert(expr test, expr? msg)

          | Import(alias* names)
          | ImportFrom(identifier? module, alias* names, int? level)

          | Global(identifier* names)
          | Nonlocal(identifier* names)
          | Expr(expr value)
          | Pass | Break | Continue

          -- XXX Jython will be different
          -- col_offset is the byte offset in the utf8 string the parser uses
          attributes (int lineno, int col_offset)

          -- BoolOp() can use left & right?
    expr = BoolOp(boolop op, expr* values)
         | BinOp(expr left, operator op, expr right)
         | UnaryOp(unaryop op, expr operand)
         | Lambda(arguments args, expr body)
         | IfExp(expr test, expr body, expr orelse)
         | Dict(expr* keys, expr* values)
         | Set(expr* elts)
         | ListComp(expr elt, comprehension* generators)
         | SetComp(expr elt, comprehension* generators)
         | DictComp(expr key, expr value, comprehension* generators)
         | GeneratorExp(expr elt, comprehension* generators)
         -- the grammar constrains where yield expressions can occur
         | Await(expr value)
         | Yield(expr? value)
         | YieldFrom(expr value)
         -- need sequences for compare to distinguish between
         -- x < 4 < 3 and (x < 4) < 3
         | Compare(expr left, cmpop* ops, expr* comparators)
         | Call(expr func, expr* args, keyword* keywords)
         | Num(object n) -- a number as a PyObject.
         | Str(string s) -- need to specify raw, unicode, etc?
         | FormattedValue(expr value, int? conversion, expr? format_spec)
         | JoinedStr(expr* values)
         | Bytes(bytes s)
         | NameConstant(singleton value)
         | Ellipsis
         | Constant(constant value)

         -- the following expression can appear in assignment context
         | Attribute(expr value, identifier attr, expr_context ctx)
         | Subscript(expr value, slice slice, expr_context ctx)
         | Starred(expr value, expr_context ctx)
         | Name(identifier id, expr_context ctx)
         | List(expr* elts, expr_context ctx)
         | Tuple(expr* elts, expr_context ctx)

          -- col_offset is the byte offset in the utf8 string the parser uses
          attributes (int lineno, int col_offset)

    expr_context = Load | Store | Del | AugLoad | AugStore | Param

    slice = Slice(expr? lower, expr? upper, expr? step)
          | ExtSlice(slice* dims)
          | Index(expr value)

    boolop = And | Or

    operator = Add | Sub | Mult | MatMult | Div | Mod | Pow | LShift
                 | RShift | BitOr | BitXor | BitAnd | FloorDiv

    unaryop = Invert | Not | UAdd | USub

    cmpop = Eq | NotEq | Lt | LtE | Gt | GtE | Is | IsNot | In | NotIn

    comprehension = (expr target, expr iter, expr* ifs, int is_async)

    excepthandler = ExceptHandler(expr? type, identifier? name, stmt* body)
                    attributes (int lineno, int col_offset)

    arguments = (arg* args, arg? vararg, arg* kwonlyargs, expr* kw_defaults,
                 arg? kwarg, expr* defaults)

    arg = (identifier arg, expr? annotation, string? type_comment)
           attributes (int lineno, int col_offset)

    -- keyword arguments supplied to call (NULL identifier for **kwargs)
    keyword = (identifier? arg, expr value)

    -- import name with optional 'as' alias.
    alias = (identifier name, identifier? asname)

    withitem = (expr context_expr, expr? optional_vars)

    type_ignore = TypeIgnore(int lineno)
}
"""

# from pprint import pprint

import hypothesis.strategies as st

from typed_ast import ast3
import string

import typing as ty

T = ty.TypeVar('T')

identifier = st.from_regex(r"\A[a-zA-Z_][a-zA-Z_0-9]*\Z")


def __optional(strategy: st.SearchStrategy[T]) -> st.SearchStrategy[ty.Optional[T]]:
    return st.one_of(st.none(), strategy)


def __many_options_from_list(ls: ty.List[ty.Type[T]]) -> st.SearchStrategy[T]:
    return st.one_of(*[st.builds(v) for v in ls])


text_no_newlines = string.printable[:-4]
type_comment = st.one_of(st.text(text_no_newlines), st.none())

expr_context = __many_options_from_list([
    ast3.Load, ast3.Store, ast3.Del, ast3.Param,
    # ast3.AugLoad, ast3.AugStore  # Aren't used in current implementation
    # for more info see:
    # https://bytes.com/topic/python/answers/845057-what-do-_ast-load-store-del-augload-augstore-param-mean
    # and: https://github.com/python/cpython/search?utf8=%E2%9C%93&q=AugLoad&type=
])

boolop = __many_options_from_list([ast3.And, ast3.Or])

operator = __many_options_from_list([
    ast3.Add, ast3.Sub, ast3.Mult, ast3.MatMult, ast3.Div, ast3.Mod, ast3.Pow,
    ast3.LShift, ast3.RShift, ast3.BitOr, ast3.BitXor, ast3.BitAnd, ast3.FloorDiv])

unaryop = __many_options_from_list([ast3.Invert, ast3.Not, ast3.UAdd, ast3.USub])

cmpop = __many_options_from_list([
    ast3.Eq, ast3.NotEq, ast3.Lt, ast3.LtE, ast3.Gt, ast3.GtE, ast3.Is, ast3.IsNot,
    ast3.In, ast3.NotIn])

Num: st.SearchStrategy[ast3.Num]
Num = st.builds(ast3.Num, st.one_of(st.floats(), st.integers()))

Str: st.SearchStrategy[ast3.Str]
Str = st.builds(ast3.Str, st.text())

Name: st.SearchStrategy[ast3.Name]
Name = st.builds(ast3.Name, identifier, expr_context)

arg = st.deferred(lambda: st.builds(ast3.arg, identifier, __optional(expr), type_comment))

Ellipsis = st.builds(ast3.Ellipsis)


@st.composite
def arguments(
        draw: ty.Callable[[st.SearchStrategy], ty.Any],
) -> ast3.arguments:
    args = draw(st.lists(arg))
    defaults = draw(st.lists(expr, max_size=len(args)))
    vararg = draw(__optional(arg))
    kwonlyargs = draw(st.lists(arg, max_size=0 if vararg is None else None))  # type: ignore
    n_kwon = len(kwonlyargs)
    kw_defaults = draw(st.lists(__optional(expr), min_size=n_kwon, max_size=n_kwon))
    kwarg = draw(__optional(arg))
    return ast3.arguments(args, vararg, kwonlyargs, kw_defaults, kwarg, defaults)


@st.composite
def BinOp(
        draw: ty.Callable[[st.SearchStrategy], ty.Any],
        expr_: st.SearchStrategy,
) -> ast3.BinOp:
    left = draw(expr_)
    right = draw(expr_)
    op = draw(operator)
    return ast3.BinOp(left, op, right)


@st.composite
def Dict(
        draw: ty.Callable[[st.SearchStrategy], ty.Any],
        keys: ty.Optional[st.SearchStrategy] = None,
        vals: ty.Optional[st.SearchStrategy] = None,
) -> ast3.Dict:
    if vals is None:
        if keys is not None:
            vals = keys
        else:
            vals = expr
    if keys is None:
        keys = expr
    xs = draw(st.lists(keys))
    n = len(xs)
    ys = draw(st.lists(vals, min_size=n, max_size=n))
    return ast3.Dict(xs, ys)


def List(exp: st.SearchStrategy) -> st.SearchStrategy[ast3.List]:
    return st.builds(ast3.List, st.lists(exp), expr_context)


expr: st.SearchStrategy[ast3.expr]
expr = st.recursive(Num | Str | Name | Ellipsis,
                    lambda exp:  # type: ignore
                    Dict(exp)
                    | BinOp(exp)
                    | List(exp))


# stmt's

Pass = st.builds(ast3.Pass)
Break = st.builds(ast3.Break)
Continue = st.builds(ast3.Continue)

Expr: st.SearchStrategy[ast3.Expr]
Expr = st.builds(ast3.Expr, expr)


def For(
        exp: st.SearchStrategy,
        stm: st.SearchStrategy,
        in_exp: ty.Optional[st.SearchStrategy] = None,
        type_comment: st.SearchStrategy[ty.Optional[str]] = type_comment,
        empty_else: bool = False
) -> st.SearchStrategy[ast3.For]:
    if in_exp is None:
        in_exp = exp
    if empty_else:
        orelse = st.lists(stm, max_size=0)
    else:
        orelse = st.lists(stm)
    return st.builds(ast3.For, exp, in_exp, st.lists(stm, min_size=1), orelse, type_comment)


def FunctionDef(
        exp: st.SearchStrategy,
        stm: st.SearchStrategy,
) -> st.SearchStrategy[ast3.FunctionDef]:
    return st.builds(ast3.FunctionDef,
                     identifier, arguments(), stm, st.lists(exp), __optional(exp), type_comment)


stmt = st.recursive(Pass | Break | Continue | Expr,
                    lambda stm:  # type: ignore
                    For(expr, stm)
                    | FunctionDef(expr, stm))


if __name__ == '__main__':
    # print(identifier.example())
    # print()
    # ex = Dict().example()
    # ex = expr.example()
    # ex = stmt.example()
    # ex = ast3.fix_missing_locations(stmt.example())
    # ex = For(List(Num), Pass, in_exp=Name, type_comment=st.none(), empty_else=True).example()
    # ex = arg.example()
    # ex = arguments().example()
    ex = FunctionDef(expr, stmt).example()
    from tensorlint.translate.tools import pprint_ast_expr
    pprint_ast_expr(ex)
    from typed_astunparse import unparse
    print(unparse(ex))
