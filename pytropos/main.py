#!/usr/bin/env python3
"""Program entry point"""

import argparse
import ast
import sys
from typed_ast import ast3
from typing import TYPE_CHECKING
import traceback
import code

from pytropos.ast_transformer import \
    typed_ast3_to_ast, PytroposTransformer, AstTransformerError
from pytropos import metadata
import pytropos.debug_print as debug_print
from pytropos.debug_print import dprint, derror
from pytropos.internals.errors import TypeCheckLogger

if TYPE_CHECKING:
    from typing import List, Optional
    from typing import Dict, Any, Tuple  # noqa: F401
    from types import CodeType

    from pytropos import Store


banner = r"""Welcome to
.___      _
| _ \_  _| |_ _ _ ___.____  ___.__.
|  _/ || |  _| '_/ _ \ '_ \/ _ (_-<
|_|  \_, |\__|_| \___/ .__/\___/__/
     |__/            |_|
An abstract interpreter for Python
Type `:?` or `:help` for help
"""

exitmsg = "Bye!! :D"


def main(argv: 'List[str]') -> int:
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

    repl_or_file = arg_parser.add_mutually_exclusive_group()

    repl_or_file.add_argument(
        '-r', '--repl',
        action='store_true',
        default=False,
        help='Runs Pytropos REPL'
    )

    repl_or_file.add_argument(
        'file',
        nargs='?',
        type=argparse.FileType('r'),
        help='File to analyse')

    args_parsed = arg_parser.parse_args(args=argv[1:])

    # Highest level of verbosity is 3
    debug_print.verbosity = 3 if args_parsed.verbose > 3 else args_parsed.verbose

    if args_parsed.repl:
        PytroposConsole().interact(banner=banner, exitmsg=exitmsg)
        return 0
    else:
        cursorline = args_parsed.check_line  # type: Optional[int]

        file = args_parsed.file
        exitcode = run_pytropos(file.read(), file.name, cursorline)[0]
        return exitcode


def run_pytropos(  # noqa: C901
        file: str,
        filename: str,
        cursorline: 'Optional[int]' = None,
        console: bool = False,
        pt_globals: 'Optional[Dict[str, Any]]' = None
) -> 'Tuple[int, Optional[Store]]':
    dprint("Starting pytropos", verb=1)

    dprint("Parsing and un-parsing a python file (it should preserve all type comments)", verb=2)

    if debug_print.verbosity > 1:
        try:
            from typed_astunparse import unparse
        except ModuleNotFoundError:
            print("Sorry! You need to install `typed_astunparse` for bigger verbosity levels.\n"
                  "Note: If you are using python 3.7 we recommend you to install \n"
                  "      `typed_astunparse` with `pip install -r git_requirements.txt` \n"
                  "      (you can find `git_requirements.txt` in {})\n".format(metadata.url),
                  file=sys.stderr)
            exit(1)

    # Parsing file
    ast_: ast3.Module
    try:
        ast_ = ast3.parse(file, filename=filename)  # type: ignore
    except SyntaxError as msg:
        derror(f"{msg.filename}:{msg.lineno}:{msg.offset-1}: {type(msg).__name__}: {msg.msg}")
        return (2, None)
    except (OverflowError, ValueError) as msg:
        derror(f"{filename}::: {type(msg).__name__}")
        return (2, None)

    if debug_print.verbosity > 1:
        dprint("Original file:", verb=2)
        dprint("AST dump of original file:", ast3.dump(ast_), verb=3)
        dprint(unparse(ast_), verb=2)

    # Converting AST (code) into Pytropos representation
    newast: ast3.Module
    try:
        newast = PytroposTransformer(  # type: ignore
            filename,
            cursorline=cursorline,
            console=console
        ).visit(ast_)
    except AstTransformerError as msg:
        derror("Sorry it seems Pytropos cannot run the file. Pytropos doesn't support "
               "some Python characteristic it uses right now. Sorry :(")
        # traceback.print_exc()
        derror(msg)
        return (2, None)

    if debug_print.verbosity > 1:
        dprint("Modified file:", verb=2)
        dprint("AST dump of modified file:", ast3.dump(newast), verb=3)
        dprint(unparse(newast), verb=2)

    newast_py = ast.fix_missing_locations(typed_ast3_to_ast(newast))
    # TODO(helq): add these lines of code for optional debugging
    # import astpretty
    # astpretty.pprint(newast_py)
    newast_comp = compile(newast_py, '<generated type checking ast>', 'exec')

    exitvalues = run_transformed_type_checking_code(newast_comp, pt_globals)
    TypeCheckLogger.clean_sing()

    dprint("Closing pytropos", verb=1)

    return exitvalues


def run_transformed_type_checking_code(
        newast_comp: 'CodeType',
        pt_globals: 'Optional[Dict[str, Any]]'
) -> 'Tuple[int, None[Store]]':
    if pt_globals is None:
        pt_globals = {}

    # from pytropos.internals.tools import NonImplementedPT
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
        derror(pt_globals['st'], end='\n\n', verb=2)

        traceback.print_exc()
        return (2, None)

    store = pt_globals['st']

    if debug_print.verbosity == 2:
        derror("\nLast computed variables values (Store):", verb=2)
        derror(store, end='\n\n', verb=2)

    if debug_print.verbosity == 3:
        derror("\nLast computed variables values (Store):", verb=3)
        derror("Store({", verb=3)
        for i, v in store.items():
            derror(f"  {i!r}: PythonValue({v.val}),", verb=3)
        derror("})\n", verb=3)

    if len(TypeCheckLogger().warnings) > 0:
        derror(TypeCheckLogger())
        return (1, store)
    else:
        dprint('No type checking error found.', verb=1)
        dprint('I wasn\'t able to find any error in the code, though there may be some (sorry)',
               verb=2)
    return (0, store)


def entry_point() -> None:
    """Zero-argument entry point for use with setuptools/distribute."""
    raise SystemExit(main(sys.argv))


class PytroposConsole(code.InteractiveConsole):
    # def raw_input(self, prompt: str = "") -> str:
    #     got = super().raw_input(prompt)
    #     print(got)
    #     return got
    locals = None  # type: Dict[str, Any]

    def __init__(self, locals: 'Optional[dict]' = None) -> None:
        super().__init__(locals)
        import pytropos as pt
        import pytropos.internals.values.python_values as pv
        import pytropos.internals.values.builtin_values as bv

        self.locals['pt'] = pt
        self.locals['st'] = store = pt.Store()
        self.locals['fn'] = '<console>'

        def print_console(v: pv.PythonValue) -> None:
            store['_'] = v  # The value executed is saved on Store
            if isinstance(v.val, bv.NoneType):
                return
            print(v)

        self.locals['print_console'] = print_console

        self.help = \
            "Interpreter special commands:\n\n" \
            ":?   :help      Prints this help\n" \
            ":in  :inspect   Access to underlying objects representation" \
            " in a regular Python environment\n" \
            ":st  :store     Prints all variables values (ie, globals())\n"

    def runsource(self,
                  source: str,
                  filename: str = "<input>",
                  symbol: str = "single"
                  ) -> bool:

        if source and source[0] == ':':
            if source.strip() in [':inspect', ':in']:
                code.InteractiveConsole(locals=self.locals).interact()
                return False
            elif source.strip() in [':store', ':st']:
                print(self.locals['st'])
                return False
            elif source.strip() in [':help', ':?']:
                print(self.help)
                return False
            else:
                print(self.help)
                return False

        try:
            code_ = self.compile(source, filename, symbol)  # type: ignore
        except (OverflowError, SyntaxError, ValueError):
            # Case 1
            self.showsyntaxerror(filename)
            return False

        if code_ is None:
            # Case 2
            return True

        # print(source)
        # Case 3
        run_pytropos(source,
                     '<console>',
                     console=True,
                     pt_globals=self.locals)
        return False


if __name__ == '__main__':
    entry_point()
