# from pytest import raises
import pytest

from pytropos.translate import to_python_ast, PytroposTransformer
from pytropos.internals.vault import Vault

from typed_ast import ast3
import ast

from typing import Any, Tuple, Optional, Dict

# The parametrize function is generated, so this doesn't work:
#
#     from pytest.mark import parametrize
#
parametrize = pytest.mark.parametrize


class TestVault(object):
    @parametrize('fileargs', [  # type: ignore
        ('tests/example_code/regression/01-local_variable_isnot_global.py', None),
        # ('tests/example_code/regression/02-nonlocal_variable_is_not_global.py', 5),
        ('tests/example_code/regression/03-del_local_variable_not_global.py', 10),
        ('tests/example_code/regression/04-local_variable_isnot_global2.py', 20),
        # ('tests/example_code/regression/05-del_nonlocal_variable_not_global.py', 12),
    ])
    def test_a_local_variable_shouldnt_be_saved_in_global_space(
            self, fileargs: Tuple[str, Optional[int]], capsys: Any
    ) -> None:
        filepath, i_value = fileargs

        ast_ = ast3.parse(open(filepath, 'r').read(), filename=filepath)
        newast: ast3.Module
        newast = PytroposTransformer(filepath).visit(ast_)  # type: ignore

        newast_py = ast.fix_missing_locations(to_python_ast(newast))
        newast_comp = compile(newast_py, '<generated type checking ast>', 'exec')

        pt_globals: Dict[str, Any] = {}
        exec(newast_comp, pt_globals)
        assert 'vau' in pt_globals

        vau: Vault = pt_globals['vau']

        if i_value is None:
            assert 'i' not in vau
        else:
            assert 'i' in vau and vau['i'].n == i_value
