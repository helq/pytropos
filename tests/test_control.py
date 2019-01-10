from hypothesis import given
import hypothesis.strategies as st

import pytropos as pt
from pytropos import Store  # noqa: F401
import pytropos.internals.control.execute as execute
from pytropos.internals.values.builtin_values import Int
from pytropos.internals.values.python_values import PythonValue
import pytropos.internals.values.python_values as pv

from .common_strategies import st_any_pv


class TestIf:
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


class TestWhile:
    @given(st.integers(min_value=0, max_value=execute.MAX_LOOPS*2))
    def test_running_simple_loop(
            self,
            num: int
    ) -> None:
        """
        This test simulates the transformation of the following piece of code:

        > i = 0
        > b = 0
        > while i > num:
        >    b += i
        >    i += 1
        """

        st = pt.Store()

        st['num'] = pv.int(num)
        st['i'] = pv.int(0)
        st['b'] = pv.int(0)

        def while_qst(st: Store) -> PythonValue:
            return st['i'].lt(st['num'])  # type: ignore

        def while_(st: Store) -> Store:
            st['b'] = st['b'].add(st['i'])
            st['i'] = st['i'].add(pv.int(1))
            return st

        st = pt.runWhile(st, while_qst, while_)

        assert isinstance(st['i'].val, Int)
        assert isinstance(st['b'].val, Int)

        if num < execute.MAX_LOOPS:
            assert isinstance(st['i'].val.val, int)
            assert st['i'].val.val == num
            assert isinstance(st['b'].val.val, int)
            assert st['b'].val.val == num*(num-1)//2
        else:
            assert st['i'].val.is_top()
            assert st['b'].val.is_top()
