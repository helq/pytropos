"""
This module defines what a typing error contains. Any error (or warning) found at
typechecking should be added either to `errors` or `warnings`.
"""

from .tools import Pos, Singleton

from typing import Optional
from typing import List, Tuple  # noqa: F401
import typing as ty  # noqa: F401

__all__ = ['TypeCheckLogger']


WarningType = str

# Warning scheme:
# W0__ : Builtin warning, something may fail
# E0__ : Builtin error, the operation will fail
# W2__ : A warning on an attribute that doesn't exists
# W5__ : A warning with some external library (user defined)
# E5__ : Error with some external library (user defined)
# NOIDEA : Error not yet classified

# Table of known errors:
# *Deprecated
# W001*: Weird return value: Expected int or float but got ...
# E001: ZeroDivisionError
# E002: ValueError
# E003: OverflowError
# E009: TypeError: unsopported operand type(s)

# W201: Global variable not set
# W202: Local variable not set
# W203: Non-local variable not set
# W204: No attribute with that name in module
# W212: Trying to delete already deleted local variable
# W213: Trying to delete already deleted non-local variable


class TypeCheckLogger(object, metaclass=Singleton):
    def __init__(self) -> None:
        self.warnings = []  # type: List[Tuple[WarningType, str, Optional[Pos]]]

    def new_warning(self, err_code: str, msg: WarningType, pos: Optional[Pos]) -> None:
        self.warnings.append(
            (err_code, msg, pos)
        )

    def __str__(self) -> str:
        return '\n'.join(map(_warning_to_str, self.warnings))


def _warning_to_str(warn: Tuple[WarningType, str, Optional[Pos]]) -> str:
    # TODO(helq): add file to the stuff to the stuff position
    warntype, msg, pos = warn
    if pos is None:
        return "<file-unknown>::: {warntype} {msg}".format(
            warntype=warntype,
            msg=msg
        )
    pos_in_file, file = pos
    if pos_in_file is None:
        return "{file}::: {warntype} {msg}".format(
            file=file,
            warntype=warntype,
            msg=msg
        )
    else:
        lineno, col = pos_in_file
        return "{file}:{lineno}:{col}: {warntype} {msg}".format(
            file=file,
            lineno=lineno,
            col=col,
            warntype=warntype,
            msg=msg
        )
