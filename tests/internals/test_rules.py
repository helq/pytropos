from pytropos.internals.values.base import Any, AbstractValue
from pytropos.internals.values.builtin_values import Int, Float
from pytropos.internals.rules import congruent, unite

import hypothesis.strategies as st
from hypothesis import given
from tools import almost_any_value

Ints_st = st.builds(Int, st.one_of(st.integers(), st.none()))
Floats_st = st.builds(Float, st.one_of(st.floats(), st.none()))


class TestCongruent(object):
    """Testing some basic properties of congruent"""

    @given(almost_any_value)
    def test_anything_with_Any_is_always_true(self, val: AbstractValue) -> None:
        """? ~ x  is always true"""
        assert congruent(Any(), val)
        assert congruent(val, Any())

    @given(almost_any_value)
    def test_anything_is_congruent_with_itself(self, val: AbstractValue) -> None:
        """W(n) ~ W(n)  is always true"""
        assert congruent(val, val)


class TestUnite(object):
    @given(almost_any_value)
    def test_anything_unites_with_Any(self, val: AbstractValue) -> None:
        """unite(?, x) = ?"""
        assert isinstance(unite(val, Any()), Any)
        assert isinstance(unite(Any(), val), Any)

    @given(Ints_st, Ints_st)
    def test_unite_same_class_preserved_Int(self, val1: Int, val2: Int) -> None:
        """unite(Int(), Int()) = Int()"""
        assert type(unite(val1, val2)) is Int

    @given(Floats_st, Floats_st)
    def test_unite_same_class_preserved_Float(self, val1: Float, val2: Float) -> None:
        """unite(Float(), Float()) = Float()"""
        assert type(unite(val1, val2)) is Float

    @given(almost_any_value, almost_any_value)
    def test_different_values_give_Any(self, val1: AbstractValue, val2: AbstractValue) -> None:
        """unite(W(), W()) = W()"""
        if type(val1) is not type(val2):
            assert type(unite(val1, val2)) is Any
        else:
            assert type(unite(val1, val2)) is type(val1)
