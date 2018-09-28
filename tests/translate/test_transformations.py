from hypothesis import given
# from hypothesis import reproduce_failure
# from pytest import raises
# import pytest

from typed_ast import ast3
# import typing as ty

from pytropos.translate import PytroposTransformer

import pytropos.hypothesis_strategies.typed_ast as st_ast

trans = PytroposTransformer("<file>")


class TestTransformations(object):
    @given(st_ast.Num)
    def test_num_transformation(self, num: ast3.Num) -> None:
        new_ast = trans.visit_Num(num)
        assert new_ast is not None
        assert not isinstance(new_ast, list)
        assert isinstance(new_ast, ast3.Call)
        assert isinstance(new_ast.func, ast3.Attribute)
        assert isinstance(new_ast.func.value, ast3.Name)
        assert new_ast.func.value.id == 'pt'
