# This file is run by pytest

from tensorlint.internals.values import Int, Float, Any, Str, Value
from hypothesis import given
import hypothesis.strategies as st
# from hypothesis import infer

import tensorlint.internals.operations as tlo
import operator as ops
# from itertools import product

from typing import Optional
import typing as ty

ints_st = st.one_of(st.integers(), st.none())
floats_st = st.one_of(st.floats(), st.none())  # type: ignore

value_ops = [
    (ops.add, tlo.add),  # type: ignore
    (ops.mul, tlo.mul)   # type: ignore
]


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
            assert op(i, j) == vop(Int(i), Int(j)).n

    # @given(i=infer, j=infer)
    @given(st.builds(Int, ints_st),
           st.builds(Int, ints_st))
    def test_int_adding(self, i: Int, j: Int) -> None:
        """
        Any value that implements add and mul must preserve the original
        value, ie:
        Int(5) + Int() must be an Int
        """
        for op, vop in value_ops:
            assert isinstance(vop(i, j), Int)

    @given(st.floats(allow_nan=False, allow_infinity=False),  # type: ignore
           st.floats(allow_nan=False, allow_infinity=False))  # type: ignore
    def test_op_float(self, i: float, j: float) -> None:
        """
        This test basically checks that doing something like this:
        Int(3) + Int(5) == Int(8)
        for all operations (+*/...) and Values
        """
        for op, vop in value_ops:
            assert op(i, j) == vop(Float(i), Float(j)).n

    @given(ints_st, ints_st)
    def test_float_adding(self, i: Optional[float], j: Optional[float]) -> None:
        """
        Any value that implements add and mul must preserve the original
        value, ie:
        Int(5) + Int() must be an Int
        """
        for op, vop in value_ops:
            assert isinstance(vop(Float(i), Float(j)), Float)

    # TODO(helq): in the future it shouldn't not handle nans and infs
    @given(st.integers(), st.floats(allow_nan=False, allow_infinity=False))  # type: ignore
    def test_float_and_ints_comform_to_baseline_python(
            self, i: int, j: float) -> None:
        for op, vop in value_ops:
            assert op(i, j) == vop(Int(i), Float(j)).n
            assert op(j, i) == vop(Float(j), Int(i)).n

    @given(ints_st, floats_st)
    def test_float_from_operating_int_with_float(
            self, i: Optional[int], j: Optional[float]) -> None:
        for op, vop in value_ops:
            assert isinstance(vop(Int(i), Float(j)), Float)

    @given(ints_st, floats_st)
    def test_none_affects_everything(
            self, i: Optional[int], j: Optional[float]) -> None:
        for op, vop in value_ops:
            res  = vop(Int(i), Float(j)).n is None
            res2 = vop(Float(j), Int(i)).n is None
            is_i_or_j_none = (i is None) or (j is None)
            assert (is_i_or_j_none == res == res2)


almost_anything = \
    st.one_of(
        st.floats(),  # type: ignore
        st.integers(),
        st.none(),
        st.characters(),
        st.binary()
    )

almost_any_value = \
    st.one_of(
        st.builds(Int, st.integers()),
        st.builds(Float, st.floats()),  # type: ignore
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
