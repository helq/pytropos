from hypothesis import given
# from hypothesis import reproduce_failure
# from pytest import raises
# import pytest

from typed_ast import ast3
# import typing as ty

from tensorlint.translate.translator import TransformationsClass

import tensorlint.hypothesis_strategies.typed_ast as st_ast

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from tensorlint.translate.base import AddParams  # noqa: F401

trans = TransformationsClass("<file>")


class TestTransformations(object):
    @given(st_ast.expr)
    def test_num_transformation(self, num: ast3.expr) -> None:
        params = {}  # type: AddParams
        ast_trans = trans.num_transformation(num, params)
        if isinstance(num, ast3.Num):
            assert ast_trans is not None
            [(new_ast, newparams)] = ast_trans
            assert isinstance(new_ast, ast3.Call)
            assert isinstance(new_ast.func, ast3.Attribute)
            assert isinstance(new_ast.func.value, ast3.Name)
            assert new_ast.func.value.id == 'tl'
        else:
            assert ast_trans is None
