from hypothesis import given

from .common_strategies import st_any_pv

import pytropos as pt
from pytropos import Store  # noqa: F401
from pytropos.internals.values.python_values import PythonValue


class TestInt:
    @given(st_any_pv, st_any_pv)
    def test_running_if_with_booltop_is_the_same_as_joining(
            self,
            i: PythonValue,
            j: PythonValue
    ) -> None:
        """
        This test simulates the transformation of the following piece of code:

        > if d:
        >    b = 2
        > else:
        >    b = 5
        """

        st = pt.Store()

        def if_(st):
            # type: (Store) -> Store
            st['b'] = i
            return st

        def else_(st):
            # type: (Store) -> Store
            st['b'] = j
            return st

        if_qst = st['d']

        st = pt.runIf(st, if_qst, if_, else_)

        val_b = st['b']

        assert val_b == i.join(j)

    @given(st_any_pv, st_any_pv)
    def test_running_if_with_booltop_is_the_same_as_joining_noelse(
            self,
            i: PythonValue,
            j: PythonValue
    ) -> None:
        """
        This test simulates the transformation of the following piece of code:

        > b = 2
        > if d:
        >    b = 5
        """

        st = pt.Store()

        st['b'] = i

        def if_(st):
            # type: (Store) -> Store
            st['b'] = j
            return st

        if_qst = st['d']

        st = pt.runIf(st, if_qst, if_)

        val_b = st['b']

        assert val_b == i.join(j)
