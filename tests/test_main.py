import glob
from pytest import raises
import pytest
from os import path
from typing import Any, Tuple, Dict, Optional

from pytropos import metadata
import pytropos.main as main
from pytropos.internals.errors import TypeCheckLogger
from pytropos.internals.values.python_values import PythonValue

# The parametrize function is generated, so this doesn't work:
#
#     from pytest.mark import parametrize
#
parametrize = pytest.mark.parametrize

inputs = glob.glob('tests/inputs/??-*.py')


class TestMain(object):
    @parametrize('helparg', ['-h', '--help'])  # type: ignore
    def test_help(self, helparg: str, capsys: Any) -> None:
        with raises(SystemExit) as exc_info:
            main.main(['progname', helparg])
        out, err = capsys.readouterr()  # type: Tuple[str, str]
        # Should have printed some sort of usage message. We don't
        # need to explicitly test the content of the message.
        assert 'usage' in out
        # Should have used the program name from the argument
        # vector.
        assert 'progname' in out
        # Should exit with zero return code.
        assert exc_info.value.code == 0

    @parametrize('versionarg', ['-V', '--version'])  # type: ignore
    def test_version(self, versionarg: str, capsys: Any) -> None:
        with raises(SystemExit) as exc_info:
            main.main(['progname', versionarg])
        out, err = capsys.readouterr()  # type: Tuple[str, str]
        # Should print out version.
        assert out == '{0} {1}\n'.format(metadata.project, metadata.version)
        # Should exit with zero return code.
        assert exc_info.value.code == 0

    def _find_output_file_and_store(self, filepath: str
                                    ) -> Tuple[str, int, Optional[Dict[str, PythonValue]]]:
        """
        Takes a filepath input and returns the expected output and results of execution.

        Input example:
            'tests/inputs/01-zero-division-fail.py'
        Output file:
            'tests/inputs/outputs/01-zero-division-fail.txt'
        The results of the computation are saved on:
            'tests/inputs/outputs/01-zero-division-fail-store.py'
        """

        dir_, name = path.split(filepath)
        output_path = path.join(dir_, 'outputs', path.splitext(name)[0]+'.txt')
        result_path = path.join(dir_, 'outputs', path.splitext(name)[0]+'-store.py')
        expected_output = open(output_path, 'r').read()

        result_file = open(result_path, 'r').read()
        globals_ = {}  # type: Dict[str, Any]
        exec(result_file, globals_)

        expected_exitcode = globals_['exitcode']
        expected_store = globals_['store']

        return expected_output, expected_exitcode, expected_store

    @parametrize('filepath', inputs)  # type: ignore
    def test_fail_and_success_in_examples(
            self,
            filepath: str,
            capsys: Any
    ) -> None:
        # Cleaning type errors
        TypeCheckLogger.clean_sing()
        assert len(TypeCheckLogger().warnings) == 0

        # Getting expected values running Pytropos
        expected_output, expected_exitcode, expected_store = \
            self._find_output_file_and_store(filepath)

        # Executing Pytropos
        file = open(filepath)
        exit_exitcode, exit_store = main.run_pytropos(file.read(), file.name)
        out, err = capsys.readouterr()

        # Checking validity of execution
        assert out == expected_output
        assert exit_exitcode == expected_exitcode

        if expected_exitcode != 2:
            assert exit_store is not None
            assert expected_store is not None
            assert exit_store._global_scope == expected_store
        else:
            assert exit_store is None
            assert expected_store is None

        # there shouldn't be any trash after the generated code is executed,
        # everything should be encapsuled
        # (Note: this is an assertion to prevent a bug to be reintroduced)
        assert len(TypeCheckLogger().warnings) == 0

        # with capsys.disabled():
        #     ...
