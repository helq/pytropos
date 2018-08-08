"""
This module defines what a typing error contains. Any error (or warning) found at
typechecking should be added either to `errors` or `warnings`.
"""

import typing as ty

__all__ = ['TL_TypeError', 'errors', 'warnings']


class TL_TypeError(object):
    msg        = None  # type: str
    lineno     = None  # type: int
    col_offset = None  # type: int

    def __init__(self, msg: str, lineno: int, col_offset: int) -> None:
        self.msg        = msg
        self.lineno     = lineno
        self.col_offset = col_offset

    def __repr__(self) -> str:
        return (
            "tl.TL_TypeError(" +
            repr(self.msg) + ', ' +
            repr(self.lineno) + ', ' +
            repr(self.col_offset) +
            ')')


errors: ty.List[TL_TypeError] = []
warnings: ty.List[TL_TypeError] = []
