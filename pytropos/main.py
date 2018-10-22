#!/usr/bin/env python3
"""Program entry point"""

from __future__ import print_function

from typing import List
from typing import Dict, Any, Optional  # noqa: F401
from types import CodeType

import argparse
import sys

from pytropos import metadata
import pytropos.debug_print as debug_print
from pytropos.debug_print import dprint, derror

import traceback


def main(argv: List[str]) -> int:
    """Program entry point.

    :param argv: command-line arguments
    :type argv: :class:`list`
    """
    author_strings = []
    for name, email in zip(metadata.authors, metadata.emails):
        author_strings.append('Author: {0} <{1}>'.format(name, email))

    epilog = (
        '{project} {version}\n' +
        '\n' +
        '{authors}\n' +
        'URL: <{url}>\n'
    ).format(
        project=metadata.project,
        version=metadata.version,
        authors='\n'.join(author_strings),
        url=metadata.url)

    arg_parser = argparse.ArgumentParser(
        prog=argv[0],
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=metadata.description,
        epilog=epilog)

    arg_parser.add_argument(
        '-V', '--version',
        action='version',
        version='{0} {1}'.format(metadata.project, metadata.version))

    arg_parser.add_argument(
        '-v', '--verbose', action='count', default=0,
        help="Shows internal parameters. This option can be stacked, so `-vvv` is possible (max: 3)"
    )

    arg_parser.add_argument(
        '-c', '--check-line',
        type=int,
        default=None,
        help="Checks the values at a specific line in the code"
    )

    arg_parser.add_argument(
        'file',
        type=argparse.FileType('r'),
        help='File to analyse')

    args_parsed = arg_parser.parse_args(args=argv[1:])

    check_line = args_parsed.check_line  # type: Optional[int]

    # Highest level of verbosity is 3
    debug_print.verbosity = 3 if args_parsed.verbose > 3 else args_parsed.verbose

    dprint("Starting pytropos", verb=1)

    dprint("Parsing and un-parsing a python file (it should preserve all type comments)", verb=2)

    from typed_ast import ast3
    if debug_print.verbosity > 1:
        try:
            from typed_astunparse import unparse
        except ModuleNotFoundError:
            print("Sorry! You need to install `typed_astunparse` for bigger any verbosity level.\n"
                  "Note: If you are using python 3.7 we recommend you to install "
                  "      `typed_astunparse` with `pip install -r git_requirements.txt` "
                  "      (you can find `git_requirements.txt` in {})\n".format(metadata.url),
                  file=sys.stderr)
            exit(1)

    from pytropos.translate import to_python_ast, PytroposTransformer

    file = args_parsed.file
    ast_: ast3.Module
    ast_ = ast3.parse(file.read(), filename=file.name)  # type: ignore

    if debug_print.verbosity > 1:  # little optimization to not run dumps
        dprint("Original file:", verb=2)
        dprint("AST dump of original file:", ast3.dump(ast_), verb=3)
        dprint(unparse(ast_), verb=2)

    newast: ast3.Module
    newast = PytroposTransformer(file.name, check_line).visit(ast_)  # type: ignore

    if debug_print.verbosity > 1:
        dprint("Modified file:", verb=2)
        dprint("AST dump of modified file:", ast3.dump(newast), verb=3)
        dprint(unparse(newast), verb=2)

    import ast
    newast_py = ast.fix_missing_locations(to_python_ast(newast))
    # TODO(helq): add this lines of code for optional debugging
    # import astpretty
    # astpretty.pprint(newast_py)
    newast_comp = compile(newast_py, '<generated type checking ast>', 'exec')

    from pytropos.internals.errors import TypeCheckLogger
    exitcode = run_transformed_type_checking_code(newast_comp)
    TypeCheckLogger.clean_sing()

    dprint("Closing pytropos", verb=1)

    return exitcode


def run_transformed_type_checking_code(newast_comp: CodeType) -> int:
    pt_globals = {}  # type: Dict[str, Any]

    # from pytropos.internals.tools import NonImplementedPT
    from pytropos.internals.errors import TypeCheckLogger
    try:
        # at the module level, locals and globals are the same
        # see: https://stackoverflow.com/questions/2904274/globals-and-locals-in-python-exec
        exec(newast_comp, pt_globals)
    except Exception:
        derror("Error: An error inside pytropos has occurred, please open an issue in:")
        derror("  ", metadata.url)
        derror("Please run the code again with `-vvv` parameter")

        derror("\nType checking errors found:", verb=2)
        derror(TypeCheckLogger(), verb=2)

        derror("\nValue of variables at the moment of the failure:", metadata.url, verb=2)
        derror(pt_globals['vau'], end='\n\n', verb=2)

        traceback.print_exc()
        return 2

    derror("\nLast computed variables values (vault):", verb=2)
    derror(pt_globals['vau'], end='\n\n', verb=2)

    if len(TypeCheckLogger().warnings) > 0:
        derror(TypeCheckLogger())
        return 1
    else:
        dprint('No type checking error found.', verb=1)
        dprint('I wasn\'t able to find any error in the code, though there may be some (sorry)',
               verb=2)
    return 0


def entry_point() -> None:
    """Zero-argument entry point for use with setuptools/distribute."""
    raise SystemExit(main(sys.argv))


if __name__ == '__main__':
    entry_point()
