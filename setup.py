# -*- coding: utf-8 -*-
from __future__ import print_function

import os
import sys
import imp
import subprocess

from typing import List, Set, TYPE_CHECKING

# TODO(helq): remove
# # Python 2.6 subprocess.check_output compatibility. Thanks Greg Hewgill!
# if 'check_output' not in dir(subprocess):
#     def check_output(cmd_args, *args, **kwargs):
#         proc = subprocess.Popen(
#             cmd_args, *args,
#             stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs)
#         out, err = proc.communicate()
#         if proc.returncode != 0:
#             raise subprocess.CalledProcessError(args)
#         return out
#     subprocess.check_output = check_output

from setuptools import setup, find_packages    # noqa
from setuptools.command.test import test as TestCommand    # noqa
from distutils import spawn  # noqa

try:
    import colorama

    colorama.init()  # Initialize colorama on Windows
except ImportError:
    # Don't require colorama just for running paver tasks. This allows us to
    # run `paver install' without requiring the user to first have colorama
    # installed.
    pass

# Add the current directory to the module search path.
sys.path.insert(0, os.path.abspath('.'))

# Constants
CODE_DIRECTORY = 'tensorlint'
DOCS_DIRECTORY = 'docs'
TESTS_DIRECTORY = 'tests'
PYTEST_FLAGS = ['--doctest-modules']

use_flake8 = True

# Import metadata. Normally this would just be:
#
#     from tensorlint import metadata
#
# However, when we do this, we also import `tensorlint/__init__.py'. If this
# imports names from some other modules and these modules have third-party
# dependencies that need installing (which happens after this file is run), the
# script will crash. What we do instead is to load the metadata module by path
# instead, effectively side-stepping the dependency problem. Please make sure
# metadata has no dependencies, otherwise they will need to be added to
# the setup_requires keyword.
if TYPE_CHECKING:
    from tensorlint import metadata
else:
    metadata = imp.load_source(
        'metadata', os.path.join(CODE_DIRECTORY, 'metadata.py'))


# Miscellaneous helper functions
def get_project_files() -> List[bytes]:
    """Retrieve a list of project files, ignoring hidden files.

    :return: sorted list of project files
    :rtype: :class:`list`
    """
    if is_git_project() and has_git():
        return get_git_project_files()

    project_files = []
    for top, subdirs, files in os.walk('.'):
        for subdir in subdirs:
            if subdir.startswith('.'):
                subdirs.remove(subdir)

        for f in files:
            if f.startswith('.'):
                continue
            project_files.append(os.path.join(top, f).encode())

    return project_files


def is_git_project() -> bool:
    return os.path.isdir('.git')


def has_git() -> bool:
    return bool(spawn.find_executable("git"))


def get_git_project_files() -> List[bytes]:
    """Retrieve a list of all non-ignored files, including untracked files,
    excluding deleted files.

    :return: sorted list of git project files
    :rtype: :class:`list`
    """
    cached_and_untracked_files = git_ls_files(
        '--cached',  # All files cached in the index
        '--others',  # Untracked files
        # Exclude untracked files that would be excluded by .gitignore, etc.
        '--exclude-standard')
    uncommitted_deleted_files = git_ls_files('--deleted')

    # Since sorting of files in a set is arbitrary, return a sorted list to
    # provide a well-defined order to tools like flake8, etc.
    return sorted(cached_and_untracked_files - uncommitted_deleted_files)


def git_ls_files(*cmd_args: str) -> Set[bytes]:
    """Run ``git ls-files`` in the top-level project directory. Arguments go
    directly to execution call.

    :return: set of file names
    :rtype: :class:`set`
    """
    cmd = ['git', 'ls-files']
    cmd.extend(cmd_args)
    return set(subprocess.check_output(cmd).splitlines())


def print_success_message(message: str) -> None:
    """Print a message indicating success in green color to STDOUT.

    :param message: the message to print
    :type message: :class:`str`
    """
    try:
        import colorama
        print(colorama.Fore.GREEN + message + colorama.Fore.RESET)
    except ImportError:
        print(message)


def print_failure_message(message: str) -> None:
    """Print a message indicating failure in red color to STDERR.

    :param message: the message to print
    :type message: :class:`str`
    """
    try:
        import colorama
        print(colorama.Fore.RED + message + colorama.Fore.RESET,
              file=sys.stderr)
    except ImportError:
        print(message, file=sys.stderr)


def read(filename: str) -> str:
    """Return the contents of a file.

    :param filename: file path
    :type filename: :class:`str`
    :return: the file's content
    :rtype: :class:`str`
    """
    with open(os.path.join(os.path.dirname(__file__), filename)) as f:
        return f.read()


def _lint() -> int:
    """Run lint and return an exit code."""
    # Flake8 doesn't have an easy way to run checks using a Python function, so
    # just fork off another process to do it.

    project_python_files = [filename for filename in get_project_files()
                            if filename.endswith(b'.py')]
    common_args = [b'--exclude=docs/**']
    if use_flake8:
        call_args = \
            [b'flake8'] \
            + project_python_files
    else:
        call_args = \
            [b'pycodestyle', b'--statistics'] \
            + common_args \
            + project_python_files
    call_args = list(map(bytes.decode, call_args))  # type: ignore
    retcode = subprocess.call(call_args)
    if retcode == 0:
        print_success_message('No style errors')
    return retcode


def _test(pytest_args: List[str] = []) -> int:
    """Run the unit tests.

    :return: exit code
    """
    # ignore_dirs = ['tests/example_code']
    # Make sure to import pytest in this function. For the reason, see here:
    # <http://pytest.org/latest/goodpractises.html#integration-with-setuptools-test-commands>  # noqa
    import pytest
    # This runs the unit tests.
    # It also runs doctest, but only on the modules in TESTS_DIRECTORY.
    return pytest.main(  # type: ignore
        PYTEST_FLAGS +
        [TESTS_DIRECTORY,
         # '--ignore='+','.join(ignore_dirs),
         '--mypy'
         ] +
        pytest_args)


def _test_all() -> int:
    """Run lint and tests.

    :return: exit code
    """
    return _lint() + _test()


# The following code is to allow tests to be run with `python setup.py test'.
# The main reason to make this possible is to allow tests to be run as part of
# Setuptools' automatic run of 2to3 on the source code. The recommended way to
# run tests is still `paver test_all'.
# See <http://pythonhosted.org/setuptools/python3.html>
# Code based on <http://pytest.org/latest/goodpractises.html#integration-with-setuptools-test-commands>  # noqa
class TestAllCommand(TestCommand):  # type: ignore
    def finalize_options(self) -> None:
        TestCommand.finalize_options(self)
        # These are fake, and just set to appease distutils and setuptools.
        self.test_suite = True
        self.test_args  = []  # type: List[str]

    def run_tests(self) -> None:
        raise SystemExit(_test_all())


# See here for more options:
# <http://pythonhosted.org/setuptools/setuptools.html>
setup_dict = dict(
    name=metadata.package,
    version=metadata.version,
    author=metadata.authors[0],
    author_email=metadata.emails[0],
    maintainer=metadata.authors[0],
    maintainer_email=metadata.emails[0],
    url=metadata.url,
    description=metadata.description,
    long_description=read('README.md'),
    # Find a list of classifiers here:
    # <http://pypi.python.org/pypi?%3Aaction=list_classifiers>
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development',
    ],
    packages=find_packages(exclude=(TESTS_DIRECTORY,)),
    install_requires=([
        '',
        # your module dependencies
    ]),

    # Allow tests to be run with `python setup.py test'.
    tests_require=[
        'pytest==3.1.3',
        'mock==2.0.0',
        # 'flake8==3.4.1',
        'pycodestyle==2.3.1',
    ],
    cmdclass={'test': TestAllCommand},
    zip_safe=False,  # don't use eggs
    entry_points={
        'console_scripts': [
            'tensorlint = tensorlint.main:entry_point'
        ],
        # if you have a gui, use this
        # 'gui_scripts': [
        #     'tensorlint_gui = tensorlint.gui:entry_point'
        # ]
    }
)


def main() -> None:
    setup(**setup_dict)


if __name__ == '__main__':
    main()
