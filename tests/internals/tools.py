from tensorlint.internals.builtin_values import Int, Float, Str
from tensorlint.internals.value import Any

import hypothesis.strategies as st

__all__ = ['almost_any_value']

almost_any_value = \
    st.one_of(
        st.builds(Int),
        st.builds(Float),
        st.builds(Int, st.integers()),
        st.builds(Float, st.floats()),
        st.builds(Any),
        st.builds(Str, st.characters()),
    )
