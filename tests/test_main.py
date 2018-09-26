from pytest import raises
import pytest
from tensorlint import metadata
from tensorlint.main import main
from tensorlint.internals.errors import TypeCheckLogger

from typing import Any, Tuple
from os import path


# The parametrize function is generated, so this doesn't work:
#
#     from pytest.mark import parametrize
#
parametrize = pytest.mark.parametrize


class TestMain(object):
    @parametrize('helparg', ['-h', '--help'])  # type: ignore
    def test_help(self, helparg: str, capsys: Any) -> None:
        with raises(SystemExit) as exc_info:
            main(['progname', helparg])
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
            main(['progname', versionarg])
        out, err = capsys.readouterr()  # type: Tuple[str, str]
        # Should print out version.
        assert out == '{0} {1}\n'.format(metadata.project, metadata.version)
        # Should exit with zero return code.
        assert exc_info.value.code == 0

    @parametrize('fileargs', [  # type: ignore
        ('tests/example_code/01-adding-mypy-types-fail.py', 1),
        ('tests/example_code/02-number-inside-for-loop-fail.py', 1),
        ('tests/example_code/03-number-inside-for-loop-success.py', 0),
        ('tests/example_code/04-if-branching-fail.py', 1),
        ('tests/example_code/05-functions-fail.py', 1),
        ('tests/example_code/07-zero-division-fail.py', 1),
    ])
    def test_fail_and_success_in_examples(self, fileargs: Tuple[str, int], capsys: Any) -> None:
        filepath, expected_exit = fileargs

        # with capsys.disabled():
        #     ...
        # exit_value = main(['<progname>', '-v', filepath])
        exit_value = main(['<progname>', filepath])

        # Should exit with zero return code if everything type checked, it
        # shouldn't otherwise.
        assert exit_value == expected_exit

        # there shouldn't be any trash after the generated code is executed,
        # everything should be encapsuled
        # (Note: this is an assertion to prevent a bug to be reintroduced)
        assert len(TypeCheckLogger().warnings) == 0

        # import tensorlint.debug_print as debprint
        # with capsys.disabled():
        #     print(debprint.verbosity)

        out, err = capsys.readouterr()

        dir_, name = path.split(filepath)
        output_path = path.join(dir_, 'output', path.splitext(name)[0]+'.txt')
        expected_output = open(output_path, 'r').read()

        assert out == expected_output
        # assert err == ""
