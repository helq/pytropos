import hypothesis.strategies as st

import pytropos.internals.values as pv
from pytropos.internals.values.python_values import PythonValue


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
    st.just(pv.none()),
    st.just(PythonValue.top())
)
