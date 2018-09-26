import typing as ty
from typing import Union, Tuple, Optional, TYPE_CHECKING
from typing import List  # noqa: F401

from ..values.value import Value, Any
from ..tools import Pos
from ..errors import TypeCheckLogger

__all__ = [
    'RuleError', 'BinRules',
    'congruent', 'unite'
]

if TYPE_CHECKING:
    Bool = __builtins__.bool

BinOp = ty.Callable[[Value, Value, Optional[Pos]], Value]
UniOp = ty.Callable[[Value, Optional[Pos]], Value]

binary_operators = [
    ('add',      '+',  ('__add__',      '__radd__'     )),  # noqa: E202
    ('sub',      '-',  ('__sub__',      '__rsub__'     )),  # noqa: E202
    ('mul',      '*',  ('__mul__',      '__rmul__'     )),  # noqa: E202
    ('truediv',  '/',  ('__truediv__',  '__rtruediv__' )),  # noqa: E202
    ('floordiv', '//', ('__floordiv__', '__rfloordiv__')),  # noqa: E202
    ('mod',      '%',  ('__mod__',      '__rmod__'     )),  # noqa: E202
    ('pow',      '**', ('__pow__',      '__rpow__'     )),  # noqa: E202
    ('lshift',   '<<', ('__lshift__',   '__rlshift__'  )),  # noqa: E202
    ('rshift',   '>>', ('__rshift__',   '__rrshift__'  )),  # noqa: E202
    ('eq',       '==', ('__eq__',)),  # noqa: E202
    # ('neq',      '==', ('__neq__',)),  # noqa: E202
    # ('lt',       '<', ('__lt__',)),  # noqa: E202
    # ('gt',       '>', ('__gt__',)),  # noqa: E202
]  # type: List[Tuple[str, str, Union[Tuple[str], Tuple[str, str]]]]

unary_operators = [
    ('bool', ('__bool__',)),
    ('len', ('__len__',)),
]

all_operators = [op for op, _, _ in binary_operators]
all_operators.extend([op for op, _ in unary_operators])


# Base method definition
# def sub(valL: Value, valR: Value) -> Value:
#     if isinstance(valL, Any) or isinstance(valR, Any):
#         return Any()
#     res = binop_rules.run('__sub__', valL, valR)
#     if res is NotImplemented:
#         res = binop_rules.run('__rsub__', valR, valL)
#     if res is NotImplemented:
#         return Any()
#     return res

def __create_binop(
        dunder_ops: Union[Tuple[str], Tuple[str, str]],
        opname: str
) -> ty.Callable[[Value, Value, Optional[Pos]], Union[Value, 'NotImplemented']]:

    def binop(valL: Value, valR: Value, src_pos: Optional[Pos] = None) -> Value:
        if isinstance(valL, Any) or isinstance(valR, Any):
            return Any()

        res = binop_rules.run(dunder_ops[0], valL, valR, src_pos)  # eg, trying with __add__
        if res is NotImplemented and len(dunder_ops) > 1:
            res = binop_rules.run(dunder_ops[1], valR, valL, src_pos)  # eg, trying with __radd__
        if res is NotImplemented:
            # TODO(helq): This warning should be hidden by default!
            TypeCheckLogger().new_warning(
                "E009",
                "unsupported operand type(s) for {op}: '{leftarg}' and '{rightarg}'"
                .format(
                    op=opname,
                    leftarg=valL.python_name,
                    rightarg=valR.python_name
                ),
                src_pos)
            return Any()
        return res

    return binop


# Defining operators to export (add, sub, ...) and which dunder methods are valid
for op, sym, dunder_ops in binary_operators:
    __all__.append(op)
    globals()[op] = __create_binop(dunder_ops, sym)


class RuleError(Exception):
    pass


class BinRules(object):
    def __init__(self) -> None:
        self._rules = {}  # type: ty.Dict[str, ty.Dict[ty.Type, BinOp]]
        for _, _, rule_names in binary_operators:
            for r_name in rule_names:
                self._rules[r_name] = {}

    def addRule(self,
                rule_name: str,
                typeL: ty.Type,
                rule: BinOp
                ) -> None:

        if rule_name not in self._rules:
            raise RuleError("`{}` is not a rule I manage".format(rule_name))
        if self.isThereARule(rule_name, typeL):
            raise RuleError("overwriting rule `{}` for type (left operand) `{}`,"
                            " this isn't allowed!".format(rule_name, typeL))
        if typeL is Any:
            raise RuleError("No new rules to `Any` can be added. Any is very special in"
                            " which every operation to it results in it itself")
        assert rule_name in self._rules, "`{}` is not a rule I manage".format(rule_name)

        self._rules[rule_name][typeL] = rule

    def isThereARule(self, rule_name: str, typeL: ty.Type) -> 'Bool':
        if rule_name not in self._rules:
            return False
        return typeL in self._rules[rule_name]

    def run(self,
            rule_name: str,
            valL: Value,
            valR: Value,
            src_pos: Optional[Pos]
            ) -> ty.Union[Value, 'NotImplemented']:

        # print("running rule {} with params: {} and {}".format(rule_name, valL, valR))
        if rule_name not in self._rules:
            raise RuleError("`{}` is not a rule I manage".format(rule_name))

        # print("{}".format(self._rules))
        if rule_name not in self._rules \
           or type(valL) not in self._rules[rule_name]:
            return NotImplemented

        return self._rules[rule_name][type(valL)](valL, valR, src_pos)

    def extractRulesFromClass(self, klass: ty.Type) -> ty.Type:
        for rule_name in self._rules:
            rule_name_in_tl = rule_name.strip('_') + '_op'
            if rule_name_in_tl in dir(klass):
                self.addRule(rule_name, klass, getattr(klass, rule_name_in_tl))
        return klass


binop_rules = BinRules()


class UniRules(object):
    def __init__(self) -> None:
        self._rules = {}  # type: ty.Dict[str, ty.Dict[ty.Type, UniOp]]
        for _, rule_names in unary_operators:
            for r_name in rule_names:
                self._rules[r_name] = {}

    def addRule(self,
                rule_name: str,
                typeL: ty.Type,
                rule: UniOp,
                ) -> None:

        if rule_name not in self._rules:
            raise RuleError("`{}` is not a rule I manage".format(rule_name))
        if self.isThereARule(rule_name, typeL):
            raise RuleError("overwriting rule `{}` for type (left operand) `{}`,"
                            " this isn't allowed!".format(rule_name, typeL))
        if typeL is Any:
            raise RuleError("No new rules to `Any` can be added. Any is very special in"
                            " which every operation to it results in it itself")
        assert rule_name in self._rules, "`{}` is not a rule I manage".format(rule_name)

        self._rules[rule_name][typeL] = rule

    def isThereARule(self, rule_name: str, typeL: ty.Type) -> 'Bool':
        if rule_name not in self._rules:
            return False
        return typeL in self._rules[rule_name]

    def run(self,
            rule_name: str,
            val: Value,
            src_pos: Optional[Pos]
            ) -> ty.Union[Value, 'NotImplemented']:

        # print("running rule {} with params: {} and {}".format(rule_name, val))
        if rule_name not in self._rules:
            raise RuleError("`{}` is not a rule I manage".format(rule_name))

        # print("{}".format(self._rules))
        if rule_name not in self._rules \
           or type(val) not in self._rules[rule_name]:
            return NotImplemented

        return self._rules[rule_name][type(val)](val, src_pos)

    def extractRulesFromClass(self, klass: ty.Type) -> ty.Type:
        for rule_name in self._rules:
            rule_name_in_tl = rule_name.strip('_') + '_op'
            if rule_name_in_tl in dir(klass):
                self.addRule(rule_name, klass, getattr(klass, rule_name_in_tl))
        return klass


uniop_rules = UniRules()


def add_ops_to_global(klass: ty.Type) -> ty.Type:
    kls2 = binop_rules.extractRulesFromClass(klass)
    return uniop_rules.extractRulesFromClass(kls2)


# I don't consider subtying in this work, for simplicity purposes, no tensor derives from
# other classes (only from `object`)
def congruent(x: Value, y: Value) -> 'Bool':
    """
    Implements rules:
    x ~ ?
    ? ~ x
    x ~ x
    x ≁ y
    """
    if isinstance(x, Any) or isinstance(y, Any):
        return True

    return type(x) is type(y)


def unite(x: Value, y: Value) -> Value:
    """
    Implements unite basic rule of the type system:
    unite(?, x) = ?
    unite(x, ?) = ?
    unite(x, x) = x
    unite(x, y) = ?
    unite(W(a), W(b)) = W(unite(a,b))

    NOTE: This function doesn't assume subtyping!!!
    """
    if isinstance(x, Any) or isinstance(y, Any):
        return Any()
    if type(x) is not type(y):  # inhibiting subtyping!!
        return Any()

    return x.unite_inside(y)


if __name__ == '__main__':  # noqa: C901
    class A(Value):
        def __init__(self, n: int) -> None:
            self.n = str(n)
            self.m = 1

        def sub_op(self, other: Value) -> ty.Union[Value, 'NotImplemented']:
            if isinstance(other, A):
                ret = A(int(self.n) - int(other.n))
                ret.m += self.m + other.m + 1
                return ret
            return NotImplemented

        def __repr__(self) -> str:
            return "A(n=" + self.n + ", m=" + repr(self.m) + ")"

    @add_ops_to_global
    class B(Value):
        def __init__(self, n: int) -> None:
            self.ll = n

        def sub_op(self, other: Value) -> ty.Union[Value, 'NotImplemented']:
            if isinstance(other, B):
                return B(self.ll - other.ll)
            if isinstance(other, A):
                ret = B(self.ll - (int(other.n) * other.m))
                return ret
            return NotImplemented

        def rsub_op(self, other: Value) -> ty.Union[Value, 'NotImplemented']:
            if isinstance(other, B):
                return B(other.ll - self.ll)
            if isinstance(other, A):
                ret = B(-self.ll + (int(other.n) * other.m))
                return ret
            return NotImplemented

        def __repr__(self) -> str:
            return "B(ll=" + repr(self.ll) + ")"

    class C(Value):
        pass

    # rules.addRule('__sub__', A, A.__sub__)  # type: ignore
    binop_rules.extractRulesFromClass(A)
    print(binop_rules.run('__sub__', A(4), A(3), None))
    # print(A(4) - A(3))
    print(sub(A(4), A(3)))  # type: ignore  # noqa: F821

    print(sub(B(4), A(3)))  # type: ignore  # noqa: F821
    print(sub(A(3), B(4)))  # type: ignore  # noqa: F821

    print(sub(A(3), C()))  # type: ignore  # noqa: F821
