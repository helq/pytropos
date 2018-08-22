# This file is run by pytest

from tools import almost_any_value

from tensorlint.internals.values.builtin_values import Int, Float, Bool
from tensorlint.internals.values.value import Any, Value
from tensorlint.internals.errors import TypeCheckLogger
from tensorlint.internals.tools import Pos

import re

from pytest import raises
from hypothesis import given
import hypothesis.strategies as st

import tensorlint.internals.operations.base as tlo
import tensorlint.internals.operations.unitary as unitary
import operator as ops
import math

from typing import Optional, Union
import typing as ty

ints_st = st.one_of(st.integers(), st.none())
floats_st = st.one_of(st.floats(), st.none())
ints_floats_st = st.one_of(st.integers(min_value=-100, max_value=100),
                           st.floats(min_value=-100, max_value=100), st.none())
ints_bools_st = st.one_of(
    st.builds(Bool, st.one_of(st.booleans(), st.none())),
    st.builds(Int, ints_st)
)


zeroDivisionError = re.compile('ZeroDivisionError')
valueError = re.compile('ValueError')


def get_ops(ls: ty.List[str]) -> ty.List[ty.Tuple[ty.Any, ty.Any]]:
    return [
        (getattr(ops, op), getattr(tlo, op))
        for op in ls
    ]


value_ops = get_ops(['add', 'sub', 'mul', 'truediv', 'floordiv', 'mod'])


def check_float_equality(f1: float, f2: float) -> bool:
    if math.isnan(f1):
        return math.isnan(f2)
    elif math.isinf(f1):
        return math.isinf(f2)
    else:
        return f1 == f2


# General test for Int and Float
class TestIntFloat(object):
    @given(st.integers())
    def test_int_preserved(self, i: int) -> None:
        assert i == Int(i).n

    @given(st.floats())
    def test_float_preserved(self, i: float) -> None:
        new_val = Float(i)
        assert new_val.n is not None
        assert check_float_equality(i, new_val.n)

    @given(st.booleans())
    def test_bool_preserved(self, b: bool) -> None:
        new_val = Bool(b)
        assert new_val.n is not None
        assert new_val.n == b

    @given(st.integers(), st.integers())
    def test_op_int(self, i: int, j: int) -> None:
        """
        This test basically checks that doing something like this:
        add(Int(3), Int(5)) == Int(8)
        for operations which image is on the same initial value
        """
        for op, vop in get_ops(['add', 'sub', 'mul']):
            val = vop(Int(i), Int(j))
            py_val = op(i, j)
            assert py_val == val.n
            assert type(py_val) is type(val.n)  # noqa: E721

    @given(ints_bools_st, ints_bools_st)
    def test_op_bools_and_ints(self, i: Union[Bool, Int], j: Union[Bool, Int]) -> None:
        """
        This test basically checks that doing something like this:
        add(Int(3), Int(5)) == Int(8)
        for operations which image is on the same initial value
        """
        for op, vop in get_ops(['add', 'sub', 'mul']):
            val = vop(i, j)
            if i.n is not None and j.n is not None:
                py_val = op(i.n, j.n)
                assert py_val == val.n
                assert type(py_val) is type(val.n)  # noqa: E721
            else:
                assert val.n is None

    @given(st.integers(), st.integers())
    def test_div_int(self, i: int, j: int) -> None:
        """
        Checks correctness of division between integers.
        truediv(Int(3), Int(5)) == Int(8)
        for division operations
        """
        for op, vop in get_ops(['truediv', 'floordiv', 'mod']):
            TypeCheckLogger.clean_sing()

            val = vop(Int(i), Int(j))
            if val.n is None:
                with raises(ZeroDivisionError):
                    op(i, j)
                assert len(TypeCheckLogger().warnings) == 1
                assert zeroDivisionError.match(TypeCheckLogger().warnings[0][1])
            else:
                assert isinstance(val, (Float, Int))
                py_val = op(i, j)
                assert py_val == val.n
                assert type(py_val) is type(val.n)  # noqa: E721
                assert len(TypeCheckLogger().warnings) == 0

    # @given(i=infer, j=infer)
    @given(st.builds(Int, ints_st),
           st.builds(Int, ints_st))
    def test_int_ops(self, i: Int, j: Int) -> None:
        """
        Any value that implements add and mul must preserve the original
        value, ie:
        Int(5) + Int() must be an Int
        """
        for op, vop in get_ops(['add', 'sub', 'mul']):
            assert isinstance(vop(i, j), Int)

    @given(st.floats(), st.floats())
    def test_op_float(self, i: float, j: float) -> None:
        """
        This test basically checks that doing something like this:
        Float(3) + Float(5) == Float(8)
        for all operations (+*/...) and Values
        """
        for op, vop in value_ops:
            TypeCheckLogger.clean_sing()

            new_val = vop(Float(i), Float(j))
            if new_val.n is None:
                with raises(ZeroDivisionError):
                    op(i, j)
                assert len(TypeCheckLogger().warnings) == 1
                assert zeroDivisionError.match(TypeCheckLogger().warnings[0][1])
            else:
                assert check_float_equality(op(i, j), new_val.n)
                assert len(TypeCheckLogger().warnings) == 0

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
        for op, vop in get_ops(['add', 'sub', 'mul']):
            assert check_float_equality( op(i, j), vop(Int(i), Float(j)).n )  # noqa: E201,E202
            assert check_float_equality( op(j, i), vop(Float(j), Int(i)).n )  # noqa: E201,E202

    @given(st.integers(), st.floats())
    def test_float_and_ints_comform_to_baseline_python_divs(
            self, i: int, j: float) -> None:
        for op, vop in get_ops(['truediv', 'floordiv', 'mod']):
            TypeCheckLogger.clean_sing()

            if j == 0:
                with raises(ZeroDivisionError):
                    op(i, j)
                assert vop(Int(i), Float(j)).n is None

                assert len(TypeCheckLogger().warnings) == 1
                assert zeroDivisionError.match(TypeCheckLogger().warnings[0][1])
            else:
                assert check_float_equality( op(i, j), vop(Int(i), Float(j)).n )  # noqa: E201,E202
                assert len(TypeCheckLogger().warnings) == 0

            if i == 0:
                with raises(ZeroDivisionError):
                    op(j, i)
                assert vop(Float(j), Int(i)).n is None

                assert len(TypeCheckLogger().warnings) > 0
                assert zeroDivisionError.match(TypeCheckLogger().warnings[-1][1])
            else:
                assert check_float_equality( op(j, i), vop(Float(j), Int(i)).n )  # noqa: E201,E202

    @given(st.one_of(
        st.tuples(st.integers(min_value=0), st.integers(min_value=0)),
        st.none()
    ))
    def test_error_pos_is_correctly_passed_to_warning(self, src_pos: ty.Optional[Pos]) -> None:
        for op, vop in get_ops(['truediv', 'floordiv', 'mod']):
            TypeCheckLogger.clean_sing()
            vop(Float(1.0), Float(0.0), src_pos)
            assert len(TypeCheckLogger().warnings) == 1
            assert TypeCheckLogger().warnings[-1][2] == src_pos

    @given(ints_st, floats_st)
    def test_float_from_operating_int_with_float(
            self, i: Optional[int], j: Optional[float]) -> None:
        for op, vop in value_ops:
            assert isinstance(vop(Int(i), Float(j)), Float)
            assert isinstance(vop(Float(j), Int(i)), Float)

    @given(ints_st, floats_st)
    def test_none_affects_everything(
            self, i: Optional[int], j: Optional[float]) -> None:
        for op, vop in get_ops(['add', 'mul']):
            res  = vop(Int(i), Float(j)).n is None
            res2 = vop(Float(j), Int(i)).n is None
            is_i_or_j_none = (i is None) or (j is None)
            assert (is_i_or_j_none == res == res2)

    @given(ints_floats_st, ints_floats_st)
    def test_pow_with_some_values(
            self, i: ty.Union[int, float, None], j: ty.Union[int, float, None]
    ) -> None:
        # event('i has type {}'.format(type(i).__name__))
        # event('j has type {}'.format(type(j).__name__))
        TypeCheckLogger.clean_sing()

        val1 = Float(i) if isinstance(i, float) else Int(i)
        val2 = Int(j) if isinstance(j, int) else Float(j)

        if i is not None and j is not None:
            new_val1 = tlo.pow(val1, val2)  # type: ignore
            if isinstance(new_val1, Any):
                assert len(TypeCheckLogger().warnings) == 1
            else:
                assert ops.pow(i, j) == new_val1.n
                assert len(TypeCheckLogger().warnings) == 0

            new_val2 = tlo.pow(val2, val1)  # type: ignore
            if isinstance(new_val2, Any):
                assert len(TypeCheckLogger().warnings) > 0
            else:
                assert ops.pow(j, i) == new_val2.n
        else:
            assert isinstance(tlo.pow(val1, val2).n, Any)  # type: ignore
            assert isinstance(tlo.pow(val2, val1).n, Any)  # type: ignore

    @given(ints_bools_st,
           st.one_of(st.integers(min_value=-2000, max_value=2000), st.none()))
    def test_shifts_with_some_values(
            self, i: Union[Int, Bool], j: Optional[int]) -> None:
        TypeCheckLogger.clean_sing()

        new_val1 = tlo.lshift(i, Int(j))  # type: ignore
        new_val2 = tlo.rshift(i, Int(j))  # type: ignore

        if i.n is None or j is None:
            assert new_val1.n is None
            assert new_val2.n is None
            assert len(TypeCheckLogger().warnings) == 0
            return

        if new_val1.n is None:
            with raises(ValueError):
                ops.lshift(i.n, j)
            assert len(TypeCheckLogger().warnings) > 0
            assert valueError.match(TypeCheckLogger().warnings[0][1])
        else:
            assert ops.lshift(i.n, j) == new_val1.n

        if new_val2.n is None:
            with raises(ValueError):
                ops.rshift(i.n, j)
            assert len(TypeCheckLogger().warnings) > 0
            assert valueError.match(TypeCheckLogger().warnings[-1][1])
        else:
            assert ops.rshift(i.n, j) == new_val2.n

    @given(almost_any_value)
    def test_bools(self, i: Value) -> None:
        if isinstance(i, Any):
            assert isinstance(unitary.bool(i), Any)
        else:
            assert isinstance(unitary.bool(i), Bool)


almost_anything = \
    st.one_of(
        st.booleans(),
        st.floats(),
        st.integers(),
        st.none(),
        st.characters(),
        st.binary()
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
