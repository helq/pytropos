from pytropos.internals.values.builtin_values import Int, Float, Str, Bool
from pytropos.internals.values.value import Any

import hypothesis.strategies as st

__all__ = ['almost_any_value']

almost_any_value = \
    st.one_of(
        st.builds(Bool),
        st.builds(Int),
        st.builds(Float),
        st.builds(Int, st.integers()),
        st.builds(Float, st.floats()),
        st.builds(Any),
        st.builds(Str, st.characters()),
    )
