# This file is run by pytest

from tensorlint.internals.values import Int, Float, Any, Str, Iterable, Value
from hypothesis import given
import hypothesis.strategies as st
from hypothesis import infer

from operator import add, mul
# from itertools import product

from typing import Optional
import typing as ty

ints_st = st.one_of(st.integers(), st.none())
floats_st = st.one_of(st.floats(), st.none())

value_ops = [add, mul]

# General test for Int and Float
class TestIntFloat(object):
    @given(st.integers()) # type: ignore
    def test_val_preserved(self, i: int) -> None:
        for klass in [Int, Float]:
            assert i == klass(i).n

    @given(st.integers(), st.integers()) # type: ignore
    def test_op_int(self, i: int, j: int) -> None:
        """
        This test basically checks that doing something like this:
        Int(3) + Int(5) == Int(8)
        for all operations (+*/...) and Values
        """
        for op in value_ops:
            assert op(i,j) == op(Int(i), Int(j)).n

    # @given(i=infer, j=infer)
    @given(st.builds(Int, ints_st), # type: ignore
           st.builds(Int, ints_st))
    def test_int_adding(self, i: Int, j: Int) -> None:
        """
        Any value that implements add and mul must preserve the original
        value, ie:
        Int(5) + Int() must be an Int
        """
        for op in value_ops:
            assert isinstance(op(i, j), Int)

    @given(st.floats(allow_nan=False, allow_infinity=False), # type: ignore
           st.floats(allow_nan=False, allow_infinity=False))
    def test_op_float(self, i: float, j: float) -> None:
        """
        This test basically checks that doing something like this:
        Int(3) + Int(5) == Int(8)
        for all operations (+*/...) and Values
        """
        for op in value_ops:
            assert op(i,j) == op(Float(i), Float(j)).n

    @given(ints_st, ints_st) # type: ignore
    def test_float_adding(self, i: Optional[float], j: Optional[float]) -> None:
        """
        Any value that implements add and mul must preserve the original
        value, ie:
        Int(5) + Int() must be an Int
        """
        for op in value_ops:
            assert isinstance(op(Float(i), Float(j)), Float)

    # TODO(helq): in the future it shouldn't not handle nans and infs
    @given(st.integers(), st.floats(allow_nan=False, allow_infinity=False)) # type: ignore
    def test_float_and_ints_comform_to_baseline_python(
            self, i: int, j: float) -> None:
        for op in value_ops:
            assert op(i, j) == op(Int(i), Float(j)).n
            assert op(j, i) == op(Float(j), Int(i)).n

    @given(ints_st, floats_st) # type: ignore
    def test_float_from_operating_int_with_float(
            self, i: Optional[int], j: Optional[float]) -> None:
        for op in value_ops:
            assert isinstance( op(Int(i), Float(j)), Float )

    @given(ints_st, floats_st) # type: ignore
    def test_none_affects_everything(
            self, i: Optional[int], j: Optional[float]) -> None:
        for op in value_ops:
            res  = op(Int(i), Float(j)).n is None
            res2 = op(Float(j), Int(i)).n is None
            is_i_or_j_none = (i is None) or (j is None)
            assert ( is_i_or_j_none == res == res2 )

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

    @given(args = st.lists(almost_anything), # type: ignore
           kargs = st.dictionaries(st.characters(), almost_anything))
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

    @given(almost_any_value) # type: ignore
    def test_any_operated_with_any_other_value_results_in_any(
            self,
            value: Value
    ) -> None:
        """
        An Any object operated with any object gives us Any()
        Any() + Int(5) == Any()
        Any() + Float(None) == Any()
        """
        for op in value_ops:
            assert isinstance(op(Any(), value), Any)
            assert isinstance(op(value, Any()), Any)