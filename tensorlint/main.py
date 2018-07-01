#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Program entry point"""

from __future__ import print_function

from typing import List, Dict, Any

import argparse
import sys

from tensorlint import metadata


def main(argv : List[str]) -> int:
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
      '{authors}' +
      'URL: <{url}>)\n'
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
        'file',
        type=argparse.FileType('r'),
        help='File to analyse')

    args_parsed = arg_parser.parse_args(args=argv[1:])

    print("Hi there! this is the starting point of everything")

    print("Parsing and un-parsing a python file (it should preserve all type comments)")
    from typed_ast import ast3
    from typed_astunparse import unparse
    from tensorlint.translate import to_tensorlint, to_python_AST
    file = args_parsed.file
    ast_ = ast3.parse(file.read(), filename=file.name)
    newast = to_tensorlint( ast_ )

    print( "Original file:" )
    print( unparse( ast_ ) )
    print( "Modified file:" )
    print( unparse( newast ) )

    import ast
    newast_py = ast.fix_missing_locations( to_python_AST(newast) )
    newast_comp = compile(newast_py, '<string>', 'exec')
    tl_globals = {} # type: Dict[str, Any]
    tl_locals = {}  # type: Dict[str, Any]

    from tensorlint.internals import NonImplementedTL
    try:
        exec( newast_comp, tl_globals, tl_locals )
    except NonImplementedTL as msg:
        print("Type checking errors found")
        print( tl_locals['tl'].errors )
        raise msg
    else:
        print("Everything ok! It typechecked!")

    # print(tl_locals)

    return 0


def entry_point() -> None:
    """Zero-argument entry point for use with setuptools/distribute."""
    raise SystemExit(main(sys.argv))


if __name__ == '__main__':
    entry_point()
