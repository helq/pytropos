# This file is run by pytest

from tensorlint.internals.builtin_values import Int, Float, Str
from tensorlint.internals.value import Any, Value
from tensorlint.internals.rules import binary_operator_operations

from pytest import raises
from hypothesis import given
import hypothesis.strategies as st
# from hypothesis import infer

import tensorlint.internals.rules as tlo
import operator as ops
# from itertools import product
import math

from typing import Optional
import typing as ty

ints_st = st.one_of(st.integers(), st.none())
floats_st = st.one_of(st.floats(), st.none())


commutative_ops = [
    (getattr(ops, op), getattr(tlo, op))
    for op in ['add', 'mul']
]

value_ops = [
    (getattr(ops, op), getattr(tlo, op))
    for op, _ in binary_operator_operations
    if op not in ['pow', 'lshift', 'rshift']
]


def check_float_equality(f1: float, f2: float) -> bool:
    if math.isnan(f1):
        return math.isnan(f2)
    elif math.isinf(f1):
        return math.isinf(f2)
    else:
        return f1 == f2


def can_op_zerodivide(op: ty.Callable) -> bool:
    return (
        op is ops.truediv
        or op is ops.floordiv
        or op is ops.mod
    )


# General test for Int and Float
class TestIntFloat(object):
    @given(st.integers())
    def test_val_preserved(self, i: int) -> None:
        for klass in [Int, Float]:
            assert i == klass(i).n  # type: ignore # this is actually true for Int and Floats

    @given(st.integers(), st.integers())
    def test_op_int(self, i: int, j: int) -> None:
        """
        This test basically checks that doing something like this:
        add(Int(3), Int(5)) == Int(8)
        for all operations (+*/...) and Values
        """
        for op, vop in value_ops:
            val = vop(Int(i), Int(j))
            if isinstance(val, Any):
                with raises(Exception):
                    op(i, j)
            else:
                if isinstance(val, (Int, Float)):
                    if val.n is None:
                        with raises(Exception):
                            op(i, j)
                    else:
                        py_val = op(i, j)
                        assert py_val == val.n
                        assert type(py_val) is type(val.n)  # noqa: E721

    # @given(i=infer, j=infer)
    @given(st.builds(Int, ints_st),
           st.builds(Int, ints_st))
    def test_int_ops(self, i: Int, j: Int) -> None:
        """
        Any value that implements add and mul must preserve the original
        value, ie:
        Int(5) + Int() must be an Int
        """
        for op, vop in value_ops:
            if op in {ops.truediv}:
                assert isinstance(vop(i, j), (Int, Float, Any))
            else:
                assert isinstance(vop(i, j), Int)

    @given(st.floats(), st.floats())
    def test_op_float(self, i: float, j: float) -> None:
        """
        This test basically checks that doing something like this:
        Int(3) + Int(5) == Int(8)
        for all operations (+*/...) and Values
        """
        for op, vop in value_ops:
            if j == 0 and can_op_zerodivide(op):
                with raises(ZeroDivisionError):
                    op(i, j)
                assert vop(Float(i), Float(j)).n is None
            else:
                assert check_float_equality(op(i, j), vop(Float(i), Float(j)).n)

    @given(floats_st, floats_st)
    def test_float_adding(self, i: Optional[float], j: Optional[float]) -> None:
        """
        Any value that implements add and mul must preserve the original
        value, ie:
        Float(5) + Float() must be an Float()
        """
        for op, vop in value_ops:
            assert isinstance(vop(Float(i), Float(j)), Float)

    @given(st.integers(), st.floats())
    def test_float_and_ints_comform_to_baseline_python(
            self, i: int, j: float) -> None:
        for op, vop in value_ops:
            if j == 0 and can_op_zerodivide(op):
                with raises(ZeroDivisionError):
                    op(i, j)
                assert vop(Int(i), Float(j)).n is None
            else:
                assert check_float_equality( op(i, j), vop(Int(i), Float(j)).n )  # noqa: E201,E202

            if i == 0 and can_op_zerodivide(op):
                with raises(ZeroDivisionError):
                    op(j, i)
                assert vop(Float(j), Int(i)).n is None
            else:
                assert check_float_equality( op(j, i), vop(Float(j), Int(i)).n )  # noqa: E201,E202

    @given(ints_st, floats_st)
    def test_float_from_operating_int_with_float(
            self, i: Optional[int], j: Optional[float]) -> None:
        for op, vop in value_ops:
            assert isinstance(vop(Int(i), Float(j)), Float)
            assert isinstance(vop(Float(j), Int(i)), Float)

    @given(ints_st, floats_st)
    def test_none_affects_everything(
            self, i: Optional[int], j: Optional[float]) -> None:
        for op, vop in commutative_ops:
            res  = vop(Int(i), Float(j)).n is None
            res2 = vop(Float(j), Int(i)).n is None
            is_i_or_j_none = (i is None) or (j is None)
            assert (is_i_or_j_none == res == res2)

    @given(st.one_of(st.integers(min_value=-100, max_value=100), st.none()),
           st.one_of(st.floats(min_value=-100, max_value=100), st.none()))
    def test_pow_with_some_values(
            self, i: Optional[int], j: Optional[float]) -> None:
        if i is not None and j is not None:
            new_val1 = tlo.pow(Int(i), Float(j))  # type: ignore
            new_val2 = tlo.pow(Float(j), Int(i))  # type: ignore
            if new_val1.n is None:
                with raises(Exception):
                    ops.pow(i, j)
            elif not isinstance(new_val1, Any):
                assert ops.pow(i, j) == new_val1.n

            if new_val2.n is None:
                with raises(Exception):
                    ops.pow(j, i)
            elif not isinstance(new_val2, Any):
                assert ops.pow(j, i) == new_val2.n
        else:
            assert tlo.pow(Int(i), Float(j)).n is None  # type: ignore
            assert tlo.pow(Float(j), Int(i)).n is None  # type: ignore

    @given(st.one_of(st.integers(), st.none()),
           st.one_of(st.integers(min_value=-2000, max_value=2000), st.none()))
    def test_shifts_with_some_values(
            self, i: Optional[int], j: Optional[int]) -> None:
        new_val1 = tlo.lshift(Int(i), Int(j))  # type: ignore
        new_val2 = tlo.rshift(Int(i), Int(j))  # type: ignore

        if i is None or j is None:
            with raises(TypeError):
                ops.lshift(i, j)
            assert new_val1.n is None
            assert new_val2.n is None
            return

        if new_val1.n is None:
            with raises(ValueError):
                ops.lshift(i, j)
        else:
            assert ops.lshift(i, j) == tlo.lshift(Int(i), Int(j)).n  # type: ignore

        if new_val2.n is None:
            with raises(ValueError):
                ops.rshift(i, j)
        else:
            assert ops.rshift(i, j) == tlo.rshift(Int(i), Int(j)).n  # type: ignore


almost_anything = \
    st.one_of(
        st.floats(),
        st.integers(),
        st.none(),
        st.characters(),
        st.binary()
    )

almost_any_value = \
    st.one_of(
        st.builds(Int, st.integers()),
        st.builds(Float, st.floats()),
        st.builds(Any),
        st.builds(Str, st.characters()),
    )


class TestAny(object):
    """
    Testing all properties of Any
    """

    @given(args=st.lists(almost_anything),
           kargs=st.dictionaries(st.characters(), almost_anything))
    def test_any_is_callable(self,
                             args: ty.List[Any],
                             kargs: ty.Dict[str, Any]) -> None:
        """
        An Any object is callable, and its result is Any()
        """
        assert isinstance(Any()(), Any)
        assert isinstance(Any()(4), Any)
        assert isinstance(Any()(*args), Any)
        assert isinstance(Any()(**kargs), Any)

    @given(almost_any_value)
    def test_any_operated_with_any_other_value_results_in_any(
            self,
            value: Value
    ) -> None:
        """
        An Any object operated with any object gives us Any()
        Any() + Int(5) == Any()
        Any() + Float(None) == Any()
        """
        for op, vop in value_ops:
            assert isinstance(vop(Any(), value), Any)
            assert isinstance(vop(value, Any()), Any)
