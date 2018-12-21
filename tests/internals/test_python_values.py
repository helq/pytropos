# This file is run by pytest

# Tests left to copy from test_builtin_values.py
# - test_pow_with_some_values
# - test_bools_return_either_Any_or_Bool
# - check_Bool_out_of_eq_operation_ints
# - check_Bool_out_of_eq_operation_floats_and_ints
# - test_any_is_callable

import re
from pytest import raises
from hypothesis import given
import hypothesis.strategies as st

import operator as ops
import math

from typing import Optional, Union  # noqa: F401

import pytropos.internals.values.python_values as pv
from pytropos.internals.values.python_values import PythonValue
from pytropos.internals.values.primitive_values \
    import AbstractValue, Int, Float, Bool, ops_symbols

from pytropos.internals.errors import TypeCheckLogger
from pytropos.internals.tools import Pos  # noqa: F401

zeroDivisionError = re.compile('ZeroDivisionError')
valueError = re.compile('ValueError')

st_ints = st.one_of(st.integers(), st.none())
st_floats = st.one_of(st.floats(), st.none())
st_bools = st.one_of(st.booleans(), st.none())

st_pv_bools_ints = st.one_of(
    st.builds(pv.int, st_ints),
    st.builds(pv.bool, st_bools),
)

st_any_pv = st.one_of(
    st.builds(pv.int, st_ints),
    st.builds(pv.float, st_floats),
    st.builds(pv.bool, st_bools),
    st.just(PythonValue.top())
)


def check_float_equality(f1: float, f2: float) -> bool:
    if not isinstance(f1, float) or not isinstance(f2, float):
        return False
    if math.isnan(f1):
        return math.isnan(f2)
    elif math.isinf(f1):
        return math.isinf(f2)
    else:
        return f1 == f2


class TestInts:
    """Testing integers only"""

    @given(st.integers())
    def test_int_preserved(self, i: int) -> None:
        assert not pv.int(i).val.is_top()  # type: ignore
        assert i == pv.int(i).val.val  # type: ignore

    @given(st.integers(), st.integers())
    def test_op_int(self, i: int, j: int) -> None:
        """
        This test basically checks that doing something like this:
        add(Int(3), Int(5)) == Int(8)
        for operations which image is on the same initial value
        """
        for op in ['add', 'sub', 'mul']:
            pt_val = getattr(pv.int(i), op)(pv.int(j))
            py_val = getattr(ops, op)(i, j)
            assert py_val == pt_val.val.val
            assert type(py_val) is type(pt_val.val.val)  # noqa: E721

    @given(st.builds(pv.int, st_ints),
           st.builds(pv.int, st_ints))
    def test_int_ops(self, i: PythonValue, j: PythonValue) -> None:
        """
        Any value that implements add and mul must preserve the original
        value, ie:
        Int(5) + Int() must be an Int
        """
        for op in ['add', 'sub', 'mul']:
            val = getattr(i, op)(j)
            assert isinstance(val.val, Int)

    @given(st.integers(), st.integers())
    def test_div_int(self, i: int, j: int) -> None:
        """
        Checks correctness of division between integers.
        int(3).truediv(int(5)) == int(3/5)
        for division operations
        """
        for op in ['truediv', 'floordiv', 'mod']:
            TypeCheckLogger.clean_sing()

            pt_val = getattr(pv.int(i), op)(pv.int(j))
            if pt_val.is_top():
                with raises(ZeroDivisionError):
                    getattr(ops, op)(i, j)
                assert len(TypeCheckLogger().warnings) == 1
                assert zeroDivisionError.match(TypeCheckLogger().warnings[0][1])
            else:
                assert isinstance(pt_val.val, (Float, Int))
                py_val = getattr(ops, op)(i, j)
                assert py_val == pt_val.val.val
                assert type(py_val) is type(pt_val.val.val)  # noqa: E721
                assert len(TypeCheckLogger().warnings) == 0

    @given(st.one_of(
        st.tuples(st.integers(min_value=0), st.integers(min_value=0)),
        st.none()
    ))
    def test_error_pos_is_correctly_passed_to_warning(self, src_pos: 'Optional[Pos]') -> None:
        for op in ['truediv', 'floordiv', 'mod']:
            TypeCheckLogger.clean_sing()
            getattr(pv.int(1), op)(pv.int(0), src_pos)
            assert len(TypeCheckLogger().warnings) == 1
            assert TypeCheckLogger().warnings[-1][2] == src_pos


class TestFloats:
    """Testing floats only"""

    @given(st.floats())
    def test_float_preserved(self, i: float) -> None:
        new_val = pv.float(i)
        assert not new_val.val.is_top()  # type: ignore
        assert check_float_equality(i, new_val.val.val)  # type: ignore

    @given(st.floats(), st.floats())
    def test_op_float(self, i: float, j: float) -> None:
        """
        This test basically checks that doing something like this:
        Float(3) + Float(5) == Float(8)
        for all operations (+*/...) and Values
        """
        for op in ['add', 'sub', 'mul', 'truediv', 'floordiv', 'mod']:
            TypeCheckLogger.clean_sing()

            pt_val = getattr(pv.float(i), op)(pv.float(j))
            assert isinstance(pt_val.val, Float)
            if pt_val.val.is_top():
                with raises(ZeroDivisionError):
                    getattr(ops, op)(i, j)
                assert len(TypeCheckLogger().warnings) == 1
                assert zeroDivisionError.match(TypeCheckLogger().warnings[0][1])
            else:
                assert check_float_equality(getattr(ops, op)(i, j), pt_val.val.val)  # type: ignore
                assert len(TypeCheckLogger().warnings) == 0

    @given(st.one_of(
        st.tuples(st.integers(min_value=0), st.integers(min_value=0)),
        st.none()
    ))
    def test_error_pos_is_correctly_passed_to_warning(self, src_pos: 'Optional[Pos]') -> None:
        for op in ['truediv', 'floordiv', 'mod']:
            TypeCheckLogger.clean_sing()
            getattr(pv.float(1.0), op)(pv.float(0.0), src_pos)
            assert len(TypeCheckLogger().warnings) == 1
            assert TypeCheckLogger().warnings[-1][2] == src_pos


class TestBools:
    """Testing floats only"""

    @given(st.booleans())
    def test_bool_preserved(self, b: bool) -> None:
        new_val = Bool(b)
        assert not new_val.is_top()
        assert new_val.val is b


class TestPythonValue:
    """Testing Top operations"""

    @given(st_any_pv)
    def test_anything_operated_with_top_is_top(self, val: PythonValue) -> None:
        for op in ops_symbols.keys():
            top = PythonValue.top()
            new_val = getattr(val, op)(top)
            assert new_val.is_top()
            new_val = getattr(top, op)(val)
            assert new_val.is_top()

    @given(st.integers(), st.floats())
    def test_float_and_ints_comform_to_baseline_python(
            self, i: int, j: float) -> None:
        for op in ['add', 'sub', 'mul']:
            op_fun = getattr(ops, op)
            assert check_float_equality(
                op_fun(i, j),
                getattr(pv.int(i), op)(pv.float(j)).val.val
            )
            assert check_float_equality(
                op_fun(j, i),
                getattr(pv.float(j), op)(pv.int(i)).val.val
            )

    @given(st.integers(), st.floats())
    def test_float_and_ints_comform_to_baseline_python_divs(
            self, i: int, j: float) -> None:
        for op in ['truediv', 'floordiv', 'mod']:
            TypeCheckLogger.clean_sing()

            if j == 0.0:
                with raises(ZeroDivisionError):
                    getattr(ops, op)(i, j)
                newval = getattr(pv.int(i), op)(pv.float(j))
                assert isinstance(newval.val, (Int, Float))
                assert newval.val.is_top()

                assert len(TypeCheckLogger().warnings) == 1
                assert zeroDivisionError.match(TypeCheckLogger().warnings[0][1])
            else:
                assert check_float_equality(
                    getattr(ops, op)(i, j),
                    getattr(pv.int(i), op)(pv.float(j)).val.val)
                assert len(TypeCheckLogger().warnings) == 0

            if i == 0:
                with raises(ZeroDivisionError):
                    getattr(ops, op)(j, i)
                newval = getattr(pv.float(j), op)(pv.int(i))
                assert isinstance(newval.val, (Int, Float))
                assert newval.val.is_top()

                assert len(TypeCheckLogger().warnings) > 0
                assert zeroDivisionError.match(TypeCheckLogger().warnings[-1][1])
            else:
                assert check_float_equality(
                    getattr(ops, op)(j, i),
                    getattr(pv.float(j), op)(pv.int(i)).val.val)

    @given(st_ints, st_floats)
    def test_float_from_operating_int_with_float(
            self, i: Optional[int], j: Optional[float]) -> None:
        for op in ['add', 'sub', 'mul', 'truediv', 'floordiv', 'mod']:
            assert isinstance(getattr(pv.int(i), op)(pv.float(j)).val, Float)
            assert isinstance(getattr(pv.float(j), op)(pv.int(i)).val, Float)

    @given(st_ints, st_floats)
    def test_none_affects_everything(
            self, i: Optional[int], j: Optional[float]) -> None:
        for op in ['add', 'sub', 'mul']:
            res  = getattr(pv.int(i), op)(pv.float(j)).val.is_top()
            res2 = getattr(pv.float(j), op)(pv.int(i)).val.is_top()
            is_i_or_j_none = (i is None) or (j is None)
            assert (is_i_or_j_none == res == res2)

    @given(st_pv_bools_ints, st_pv_bools_ints)
    def test_op_bools_and_ints(self, i: PythonValue, j: PythonValue) -> None:
        """
        This test basically checks that doing something like this:
        pv.int(3).add(pv.bool(True)) == pv.int(4)
        for operations which image is on the same initial value
        """
        for op in ['add', 'sub', 'mul']:
            val = getattr(i, op)(j)
            assert isinstance(i.val, (Bool, Int))
            assert isinstance(j.val, (Bool, Int))

            if not i.val.is_top() and not j.val.is_top():
                py_val = getattr(ops, op)(i.val.val, j.val.val)
                assert py_val == val.val.val
                assert type(py_val) is type(val.val.val)  # noqa: E721
            else:
                assert not val.is_top()
                assert val.val.is_top()

    @given(st_pv_bools_ints,
           st.one_of(st.integers(min_value=-2000, max_value=2000), st.none()))
    def test_shifts_with_some_values(
            self, i: PythonValue, j: Optional[int]) -> None:
        TypeCheckLogger.clean_sing()

        new_val1 = i.lshift(pv.int(j))
        new_val2 = i.rshift(pv.int(j))

        assert not i.is_top()
        assert isinstance(i.val, AbstractValue)
        assert isinstance(new_val1.val, AbstractValue)
        assert isinstance(new_val2.val, AbstractValue)

        if i.val.is_top() or j is None:
            assert new_val1.val.is_top()
            assert new_val2.val.is_top()
            assert len(TypeCheckLogger().warnings) == 0
            return

        if new_val1.val.is_top():
            with raises(ValueError):
                ops.lshift(i.val.val, j)  # type: ignore
            assert len(TypeCheckLogger().warnings) > 0
            assert valueError.match(TypeCheckLogger().warnings[0][1])
        else:
            assert ops.lshift(i.val.val, j) == new_val1.val.val  # type: ignore

        if new_val2.val.is_top():
            with raises(ValueError):
                ops.rshift(i.val.val, j)  # type: ignore
            assert len(TypeCheckLogger().warnings) > 0
            assert valueError.match(TypeCheckLogger().warnings[-1][1])
        else:
            assert ops.rshift(i.val.val, j) == new_val2.val.val  # type: ignore
