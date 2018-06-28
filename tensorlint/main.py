#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Program entry point"""

from __future__ import print_function

from typing import List

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
    file = args_parsed.file
    mypyfile = ast3.parse(file.read(), filename=file.name)
    print( unparse( mypyfile ) )

    return 0


def entry_point() -> None:
    """Zero-argument entry point for use with setuptools/distribute."""
    raise SystemExit(main(sys.argv))


if __name__ == '__main__':
    entry_point()
